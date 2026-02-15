import { createContext, useContext, useEffect, ReactNode, useMemo, useState } from "react";
import { useAuth as useClerkAuth, useClerk, useUser } from "@clerk/clerk-react";
import { supabase } from "@/integrations/supabase/client";
import { setClerkTokenGetter, setCurrentUserId } from "@/integrations/clerk/tokenStore";

const CLERK_SUPABASE_TEMPLATE = import.meta.env.VITE_CLERK_SUPABASE_TEMPLATE;

type AppUserMetadata = {
  user_name?: string;
  avatar_url?: string;
  full_name?: string;
};

export interface AppUser {
  id: string;
  email: string | null;
  user_metadata: AppUserMetadata;
}

interface AuthContextType {
  session: null;
  user: AppUser | null;
  loading: boolean;
  signInWithGoogle: () => Promise<void>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

function mapClerkUserToAppUser(clerkUser: NonNullable<ReturnType<typeof useUser>["user"]>): AppUser {
  return {
    id: clerkUser.id,
    email: clerkUser.primaryEmailAddress?.emailAddress || null,
    user_metadata: {
      user_name: clerkUser.username || undefined,
      avatar_url: clerkUser.imageUrl || undefined,
      full_name: clerkUser.fullName || undefined,
    },
  };
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const { isLoaded: authLoaded, getToken } = useClerkAuth();
  const { isLoaded: userLoaded, user: clerkUser } = useUser();
  const clerk = useClerk();
  const [profileReady, setProfileReady] = useState(false);

  const user = useMemo(() => {
    if (!clerkUser) return null;
    return mapClerkUserToAppUser(clerkUser);
  }, [clerkUser]);

  useEffect(() => {
    setClerkTokenGetter(async () => {
      if (CLERK_SUPABASE_TEMPLATE) {
        return getToken({ template: CLERK_SUPABASE_TEMPLATE });
      }
      return getToken();
    });

    return () => {
      setClerkTokenGetter(null);
    };
  }, [getToken]);

  useEffect(() => {
    setCurrentUserId(user?.id || null);
  }, [user?.id]);

  useEffect(() => {
    let active = true;

    if (!authLoaded || !userLoaded) {
      setProfileReady(false);
      return () => {
        active = false;
      };
    }

    if (!user) {
      setProfileReady(true);
      return () => {
        active = false;
      };
    }

    const ensureProfile = async () => {
      const { error } = await supabase.from("profiles").upsert(
        {
          user_id: user.id,
          display_name: user.user_metadata.full_name || user.user_metadata.user_name || null,
          avatar_url: user.user_metadata.avatar_url || null,
        },
        { onConflict: "user_id", ignoreDuplicates: true },
      );

      if (error) {
        console.error("Profile bootstrap error:", error);
      }
    };

    ensureProfile()
      .catch((err) => {
        console.error("Profile bootstrap error:", err);
      })
      .finally(() => {
        if (active) setProfileReady(true);
      });

    return () => {
      active = false;
    };
  }, [authLoaded, userLoaded, user]);

  const loading = !authLoaded || !userLoaded || !profileReady;

  const signInWithGoogle = async () => {
    await clerk.redirectToSignIn({
      redirectUrl: "/dashboard",
    });
  };

  const signOut = async () => {
    await clerk.signOut();
  };

  return (
    <AuthContext.Provider value={{ session: null, user, loading, signInWithGoogle, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}

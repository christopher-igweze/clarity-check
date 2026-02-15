import { SignIn } from "@clerk/clerk-react";

const SignInPage = () => {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-6">
      <SignIn path="/sign-in" routing="path" forceRedirectUrl="/dashboard" />
    </div>
  );
};

export default SignInPage;

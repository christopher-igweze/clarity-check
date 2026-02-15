type TokenGetter = () => Promise<string | null>;

let currentTokenGetter: TokenGetter | null = null;
let currentUserId: string | null = null;

export function setClerkTokenGetter(getter: TokenGetter | null) {
  currentTokenGetter = getter;
}

export async function getClerkToken(): Promise<string | null> {
  if (!currentTokenGetter) return null;
  try {
    return await currentTokenGetter();
  } catch {
    return null;
  }
}

export function setCurrentUserId(userId: string | null) {
  currentUserId = userId;
}

export function getCurrentUserId(): string | null {
  return currentUserId;
}

import { SignUp } from "@clerk/clerk-react";

const SignUpPage = () => {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-6">
      <SignUp path="/sign-up" routing="path" forceRedirectUrl="/dashboard" />
    </div>
  );
};

export default SignUpPage;

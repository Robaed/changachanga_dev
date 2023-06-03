import { ArrowSmallRightIcon } from "@heroicons/react/24/solid";
import { Alert, Button, Select, TextInput } from "~/components/core";
import { AuthLayout } from "~/components/layouts";

export default function EmailVerification() {
  return (
    <AuthLayout title="">

        <div style={{ marginTop : "30%", marginBottom : "30%" }} className="p-14 mt-10 bg-white border border-gray-200 rounded-lg shadow dark:bg-gray-800 dark:border-gray-700">

            <div style={{ marginRight: "20%", marginLeft: "20%" }} className="content-center text-center">
                <p className="font-semibold text-center text-xl">Email Verification</p>
                <p className="pt-5 text-sm font-light">We've sent you a verification email. Please check your inbox and follow the instructions to verify your email.</p>
                <p className="pt-5 text-sm font-light">Haven't received the email? <a href="#0" style={{ color: "#71AE00" }}>Click here to resend</a></p>
            </div>

            <div className="flex mt-4 content-center justify-center">
                <Button variant="outline" className="mr-4">Back</Button>

                <Button type="submit">
                    <span>Continue</span>
                    <ArrowSmallRightIcon />
                </Button>
            </div>

        
        </div>

    </AuthLayout>
  );
}

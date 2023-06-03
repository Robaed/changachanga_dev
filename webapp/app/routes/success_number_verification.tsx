import { ArrowSmallRightIcon } from "@heroicons/react/24/solid";
import { Alert, Button, Select, TextInput } from "~/components/core";
import { AuthLayout } from "~/components/layouts";

import SuccessIcon from "~/assets/images/success_icon.png"

export default function SuccessPhoneNumberVerification() {
  return (
    <AuthLayout title="">

        <div style={{ margin : "16%" }} className="p-8 mt-10 bg-white border border-gray-200 rounded-lg shadow dark:bg-gray-800 dark:border-gray-700">

            <div style={{ marginRight: "16%", marginLeft: "16%" }} className="content-center text-center">
                <p className="font-semibold text-center text-xl">Phone Number Verification Successful</p>
                <p className="pt-5 text-sm font-light">Congratulations! Your phone number has been successfully verified. Your account is now fully verified and ready for use..</p>
            </div>

            <div className="flex mt-4 content-center justify-center">
                <img src={SuccessIcon}/>
            </div>

            <div className="flex mt-4 content-center justify-center">
                <Button variant="outline" className="mr-4">Back
                </Button>

                <Button type="submit">
                    <span>Continue</span>
                    <ArrowSmallRightIcon />
                </Button>
            </div>

        
        </div>

    </AuthLayout>
  );
}

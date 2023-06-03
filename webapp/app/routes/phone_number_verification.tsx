import { useState } from 'react';
import OtpInput from 'react-otp-input';

import { ArrowSmallRightIcon } from "@heroicons/react/24/solid";
import { Alert, Button, Select, TextInput } from "~/components/core";
import { AuthLayout } from "~/components/layouts";

import SuccessIcon from "~/assets/images/success_icon.png"

export default function PhoneNumberVerification() {
    const [otp, setOtp] = useState('');

  return (
    <AuthLayout title="">

        <div style={{ margin : "16%" }} className="p-8 mt-10 bg-white border border-gray-200 rounded-lg shadow dark:bg-gray-800 dark:border-gray-700">

            <div style={{ marginRight: "16%", marginLeft: "16%" }} className="content-center text-center">
                <p className="font-semibold text-center text-xl">Phone Number Verification</p>
                <p className="pt-5 text-sm font-light">We've sent you a verification code via SMS to your phone number. Please enter the code below.</p>
            </div>

            <div id='otp_inputs' className="flex mt-4 content-center justify-center">

                <OtpInput
                    value={otp}
                    onChange={setOtp}
                    numInputs={4}
                    renderSeparator={<span>-</span>}
                    renderInput={(props) => <input {...props} />}
                    />

            </div>
                <p className="flex pt-5 text-sm font-light justify-center">Haven't received the SMS? <a href="#0" style={{ color: "#71AE00" }}>Click here to resend</a></p>

            <div className="flex mt-4 content-center justify-center">
                <Button type="submit">
                    <span>Continue</span>
                    <ArrowSmallRightIcon />
                </Button>
            </div>

        
        </div>

    </AuthLayout>
  );
}

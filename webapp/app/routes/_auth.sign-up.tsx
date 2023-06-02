import { AuthLayout } from "~/components/layouts";

import { ArrowSmallRightIcon } from "@heroicons/react/24/solid";
import { ActionArgs, redirect } from "@remix-run/node";
import { Form, useActionData } from "@remix-run/react";
import { Alert, Button, Select, TextInput } from "~/components/core";
import { DEFAULT_ERROR_MESSAGE } from "~/config/constants";
import { ACCOUNT_VERIFICATION_ROUTE, SIGN_UP_ROUTE } from "~/config/routes";
import { mapValuesToOptions } from "~/utils/misc";
import { validatePassword, validatePhoneNumber } from "~/utils/validators";
import { iamService } from "~/services/iam";
import type { CreateUser } from "~/types";

// Importing custom css for Auth screens
import "~/assets/styles/auth.css"

type ActionData = {
  formError?: string;
  fieldErrors?: {
    [x: string]: string;
  };
};
export async function action({ request }: ActionArgs) {
  const formData = await request.formData();

  const full_name = formData.get("full_name");
  const id_number = formData.get("id_number");
  const email_address = formData.get("email_address");
  const phone_number = formData.get("phone_number");
  const date_of_birth = formData.get("date_of_birth");
  const gender = formData.get("gender");
  const address_line = formData.get("address_line");
  const postal_code = formData.get("postal_code");
  const password = formData.get("password");

  // validate input fields
  if (
    typeof full_name !== "string" ||
    typeof id_number !== "string" ||
    typeof email_address !== "string" ||
    typeof phone_number !== "string" ||
    typeof date_of_birth !== "string" ||
    typeof gender !== "string" ||
    typeof address_line !== "string" ||
    typeof password !== "string" ||
    typeof postal_code !== "string"
  ) {
    return { formError: "Form submitted incorrectly" };
  }

  const passwordError = validatePassword(password);
  if (passwordError) {
    return { fieldErrors: { password: passwordError } };
  }

  const phoneNumberError = validatePhoneNumber(phone_number);
  if (phoneNumberError) {
    return { fieldErrors: { phone_number: phoneNumberError } };
  }

  const user: CreateUser = {
    full_name,
    id_number,
    email_address,
    phone_number,
    date_of_birth,
    gender,
    address_line,
    postal_code,
    password,
    country_code: "KE",
    id_document_type: "NATIONAL_ID",
    nationality: "Kenyan",
  };

  try {
    await iamService.signUp(user);
    return redirect(ACCOUNT_VERIFICATION_ROUTE);
  } catch (error) {
    return {
      formError: error instanceof Error ? error.message : DEFAULT_ERROR_MESSAGE,
    };
  }
}
export default function SignUpPage() {
  const actionData = useActionData<ActionData>();
  console.log(actionData);

  return (
    <AuthLayout title="">
      <div className="p-14 mt-10 bg-white border border-gray-200 rounded-lg shadow dark:bg-gray-800 dark:border-gray-700">

        <div style={{ marginRight: "20%", marginLeft: "20%" }} className="content-center text-center">
            <p className="font-medium text-center text-xl">Please Fill in Your Details to Create Your Account</p>
            <p className="pt-5">Already have an account? <a style={{ color: "#71AE00" }} href="#0">Login</a></p>
        </div>

        <Form method="post" className="grid gap-3" action={SIGN_UP_ROUTE}>
            {actionData?.formError && (
            <Alert variant="error">{actionData.formError}</Alert>
            )}
            <TextInput
            label="Name"
            name="full_name"
            id="full_name"
            placeholder="Full Name"
            // hint="As shown on your national ID card"
            required
            />
            <TextInput
            label="Phone Number"
            type="tel"
            placeholder="Phone Number"
            name="phone_number"
            id="phone_number"
            error={actionData?.fieldErrors?.phone_number}
            required
            />
            <TextInput
            label="Email Address"
            placeholder="Email Address"
            type="email"
            name="email_address"
            id="email_address"
            required
            />
            <TextInput
            label="Password"
            name="password"
            placeholder="Password"
            id="password"
            type="password"
            hint="Should be atleast 6 characters"
            error={actionData?.fieldErrors?.password}
            required
            />
            <TextInput
            label="Confirm Password"
            placeholder="Confirm Password"
            name="password"
            id="password"
            type="password"
            error={actionData?.fieldErrors?.password}
            required
            />
            <div className="flex content-center justify-center mt-2">
                <TextInput id="default-checkbox" type="checkbox" name="terms_and_conditions" value="" className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"/>
                <span className="pl-4 text-sm">I agree to terms and conditions</span>
            </div>
            <div className="flex mt-4 content-center justify-center">
            {/* <Button variant="outline">Back</Button> */}
            <Button type="submit">
                <span>Continue</span>
                <ArrowSmallRightIcon />
            </Button>
            </div>
        </Form>
      </div>
    </AuthLayout>
  );
}

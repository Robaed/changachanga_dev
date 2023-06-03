import type { ActionArgs } from "@remix-run/node";
import { Form, Link, useActionData } from "@remix-run/react";
import { Alert, Button, TextInput } from "~/components/core";
import { AuthLayout } from "~/components/layouts";
import { DEFAULT_ERROR_MESSAGE } from "~/config/constants";
import { FORGOT_PASSWORD_ROUTE } from "~/config/routes";
import { validatePassword, validatePhoneNumber } from "~/utils/validators";
import { iamService } from "~/services/iam";

import { useState } from 'react';

import 'react-phone-number-input/style.css'
import PhoneInput from 'react-phone-number-input'

type ActionData = {
  formError?: string;
  fieldsError?: {
    username?: string;
    password?: string;
  };
};

export async function action({ request }: ActionArgs) {
  const formData = await request.formData();
  const username = formData.get("username");
  const password = formData.get("password");

  if (typeof username !== "string" || typeof password !== "string") {
    return { formError: "Form submitted incorrectly" };
  }

  // Validate username
  const usernameError = validatePhoneNumber(username);
  if (usernameError) {
    return { fieldsError: { username: usernameError } };
  }

  // Validate password
  const passwordError = validatePassword(password);
  if (passwordError) {
    return { fieldsError: { password: passwordError } };
  }

  try {
    await iamService.logIn({ username, password });
  } catch (error) {
    return {
      formError: error instanceof Error ? error.message : DEFAULT_ERROR_MESSAGE,
    };
  }
}

export default function LoginPage() {
  const actionData = useActionData<ActionData>();
  const [value, setValue] = useState()
  return (
    <AuthLayout title="">

     <div style={{ marginTop : "30%", marginBottom : "30%" }} className="p-14 mt-10 bg-white border border-gray-200 rounded-lg shadow dark:bg-gray-800 dark:border-gray-700">
        
        <div style={{ marginRight: "16%", marginLeft: "16%" }} className="content-center text-center">
            <p style={{ fontSize: "22px;" }} className="font-semibold text-center text-xl">Welcome back! Please login to your account </p>
            <p className="pt-5 text-sm font-light">We'll send an OTP to your registered phone number.</p>
        </div>
        
        <div>
            <Form className="grid gap-3" method="post">
                {actionData?.formError && (
                <Alert variant="error">{actionData.formError}</Alert>
                )}
                <PhoneInput
                label="Phone number"
                className="mt-8"
                placeholder="+254 (0722) 000-000"
                value={value}
                onChange={setValue}/>
                <div className="flex justify-center mt-8">
                    <Button type="submit">Continue</Button>
                </div>
            </Form>
        </div>
      </div>
    </AuthLayout>
  );
}

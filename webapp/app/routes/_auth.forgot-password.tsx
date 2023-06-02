import { AuthLayout } from "~/components/layouts";

import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import { Form, useLoaderData } from "@remix-run/react";
import { useEffect, useState } from "react";
import { Button, TextInput, Toast } from "~/components/core";
import { DEFAULT_ERROR_MESSAGE } from "~/config/constants";
import { FORGOT_PASSWORD_ROUTE } from "~/config/routes";
import { validatePhoneNumber } from "~/utils/validators";
import { iamService } from "~/services/iam";
import { commitSession, getSession } from "~/services/sessions";

export async function action({ request }: ActionArgs) {
  const formData = await request.formData();
  const display = formData.get("display");
  const phone_number = formData.get("phone_number");
  const otp = formData.get("otp");
  const password = formData.get("password");

  if (typeof display !== "string" || typeof phone_number !== "string") {
    return { formError: "Form submitted incorrectly" };
  }

  const phoneNumberError = validatePhoneNumber(phone_number);
  if (phoneNumberError) {
    return { fieldsError: { phone_number: phoneNumberError } };
  }

  if (display === "forgot") {
    try {
      await iamService.sendResetPasswordCode(phone_number);
      const session = await getSession(request.headers.get("Cookie"));
      session.flash("requestCodeSuccess", "true");
      return redirect(FORGOT_PASSWORD_ROUTE, {
        headers: {
          "Set-Cookie": await commitSession(session),
        },
      });
    } catch (error) {
      return {
        formError:
          error instanceof Error ? error.message : DEFAULT_ERROR_MESSAGE,
      };
    }
  }

  if (display === "reset") {
    if (typeof otp !== "string") {
      return { fieldsError: { otp: "OTP is required" } };
    }
    if (typeof password !== "string") {
      return { fieldsError: { password: "Password is required" } };
    }

    try {
      return await iamService.resetPassword({ otp, phone_number, password });
    } catch (error) {
      return {
        formError:
          error instanceof Error ? error.message : DEFAULT_ERROR_MESSAGE,
      };
    }
  }

  return null;
}

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const requestCodeSuccess = session.get("requestCodeSuccess");
  return json(
    { requestCodeSuccess },
    {
      headers: {
        "Set-Cookie": await commitSession(session),
      },
    }
  );
}
export default function ForgotPasswordPage() {
  const loaderData = useLoaderData<typeof loader>();

  const [display, setDisplay] = useState<"forgot" | "reset">("forgot");

  useEffect(() => {
    if (loaderData.requestCodeSuccess) {
      setDisplay("reset");
    }
  }, [loaderData.requestCodeSuccess]);

  return (
    <AuthLayout title="Phone Number Verification">
      <Form method="post" className="grid gap-3">
        <input type="hidden" name="display" value={display} />
        <TextInput
          label="Phone Number"
          type="tel"
          name="phone_number"
          id="phone_number"
          required
        />

        {display === "reset" && (
          <>
            <TextInput
              label="Verification Code"
              hint="Enter the verification code sent to your phone number"
              name="otp"
              id="otp"
              required
            />
            <TextInput
              label="New Password"
              hint="Password should contain more than 6 characters"
              name="password"
              id="password"
              required
            />
          </>
        )}

        <div className="mt-6">
          <Button type="submit">
            {display === "forgot" ? "Request Code" : "Reset Password"}
          </Button>
        </div>
      </Form>
      {loaderData.requestCodeSuccess && (
        <Toast label="Verification code sent successfully" variant="success" />
      )}
    </AuthLayout>
  );
}

import { AuthLayout } from "~/components/layouts";

import { ArrowSmallRightIcon } from "@heroicons/react/24/solid";
import { Form, useActionData, useLoaderData } from "@remix-run/react";
import { useEffect, useState } from "react";
import { Alert, Button, TextInput, Toast } from "~/components/core";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import { validatePhoneNumber } from "~/utils/validators";
import { DEFAULT_ERROR_MESSAGE } from "~/config/constants";
import { iamService } from "~/services/iam";
import { ACCOUNT_VERIFICATION_ROUTE } from "~/config/routes";
import { commitSession, getSession } from "~/services/sessions";

type ActionData = {
  formError?: string;
  fieldsError?: {
    phone_number?: string;
    verification_code?: string;
  };
};

export async function action({ request }: ActionArgs) {
  const formData = await request.formData();
  const display = formData.get("display");
  const phone_number = formData.get("phone_number");
  const verification_code = formData.get("verification_code");

  if (typeof display !== "string" || typeof phone_number !== "string") {
    return { formError: "Form submitted incorrectly" };
  }

  const phoneNumberError = validatePhoneNumber(phone_number);
  if (phoneNumberError) {
    return { fieldsError: { phone_number: phoneNumberError } };
  }

  if (display === "verify") {
    if (typeof verification_code !== "string") {
      return {
        fieldsError: { verification_code: "Verification code is required" },
      };
    }
    try {
      return await iamService.verifyUserPhoneNumber({
        verification_code,
        phone_number,
      });
    } catch (error) {
      return {
        formError:
          error instanceof Error ? error.message : DEFAULT_ERROR_MESSAGE,
      };
    }
  }

  if (display === "request-code") {
    try {
      await iamService.sendPhoneNumberVerificationCode(phone_number);
      const session = await getSession(request.headers.get("Cookie"));
      session.flash("requestCodeSuccess", "true");
      return redirect(ACCOUNT_VERIFICATION_ROUTE, {
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
export default function PhoneNumberVerificationPage() {
  const loaderData = useLoaderData<typeof loader>();
  const actionData = useActionData<ActionData>();

  const [display, setDisplay] = useState<"verify" | "request-code">("verify");

  useEffect(() => {
    if (loaderData.requestCodeSuccess) {
      setDisplay("verify");
    }
  }, [loaderData.requestCodeSuccess]);

  return (
    <AuthLayout title="Phone Number Verification">
      <Form method="post" className="grid gap-3">
        {actionData?.formError && (
          <Alert variant="error">{actionData.formError}</Alert>
        )}
        <input type="hidden" name="display" value={display} />
        <TextInput
          label="Phone Number"
          type="tel"
          name="phone_number"
          id="phone_number"
          error={actionData?.fieldsError?.phone_number}
          required
        />

        {display === "verify" && (
          <TextInput
            label="Verification Code"
            hint="Enter the verification code sent to your phone number"
            name="verification_code"
            id="verification_code"
            error={actionData?.fieldsError?.verification_code}
            required
          />
        )}

        {display === "verify" && (
          <div className="flex justify-end">
            <button
              className="text-sm text-[#003D4C] font-medium"
              onClick={() => setDisplay("request-code")}
              type="button"
            >
              Get Code
            </button>
          </div>
        )}
        <div className="mt-6">
          <Button type="submit">
            {display === "verify" ? (
              <>
                <span>Continue</span>
                <ArrowSmallRightIcon className="h-4 w-4" />
              </>
            ) : (
              "Request Code"
            )}
          </Button>
        </div>
      </Form>
      {loaderData.requestCodeSuccess && (
        <Toast label="Verification code sent successfully" variant="success" />
      )}
    </AuthLayout>
  );
}

import type { ActionArgs } from "@remix-run/node";
import { Form, Link, useActionData } from "@remix-run/react";
import { Alert, Button, TextInput } from "~/components/core";
import { AuthLayout } from "~/components/layouts";
import { DEFAULT_ERROR_MESSAGE } from "~/config/constants";
import { FORGOT_PASSWORD_ROUTE } from "~/config/routes";
import { validatePassword, validatePhoneNumber } from "~/utils/validators";
import { iamService } from "~/services/iam";

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
  return (
    <AuthLayout title="Login">
      <Form className="grid gap-3" method="post">
        {actionData?.formError && (
          <Alert variant="error">{actionData.formError}</Alert>
        )}
        <TextInput
          required
          label="Phone Number"
          type="tel"
          name="username"
          id="username"
          error={actionData?.fieldsError?.username}
        />
        <div className="text-right">
          <Link
            className="text-sm text-[#003D4C] font-medium"
            to={FORGOT_PASSWORD_ROUTE}
          >
            Forgot Password?
          </Link>
        </div>
        <TextInput
          required
          label="Password"
          type="password"
          name="password"
          id="password"
          error={actionData?.fieldsError?.password}
        />
        <Button type="submit">Login</Button>
      </Form>
    </AuthLayout>
  );
}

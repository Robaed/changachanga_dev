import type { Request } from "@remix-run/node";
import { redirect } from "@remix-run/node";
import { USER_COOKIE } from "~/config/constants";
import {
  ACCOUNT_VERIFICATION_ROUTE,
  HOME_ROUTE,
  LOGIN_ROUTE,
} from "~/config/routes";
import { api, getApiErrorMessage } from "~/utils/axios";
import type {
  CreateUser,
  LoginDetails,
  LoginResponse,
  OtpVerificationResponse,
  PhoneNumberVerification,
  ResetPasswordResponse,
  User,
  UserCookie,
} from "~/types";
import { commitSession, destroySession, getSession } from "./sessions";

class IamService {
  /** Log in user */
  async logIn({ username, password }: LoginDetails) {
    try {
      const data: Record<string, string> = {
        username,
        password,
        grant_type: "password",
        scope: "",
        client_id: "",
        client_secret: "",
      };
      const formData = new URLSearchParams();
      for (const key in data) {
        formData.append(key, data[key]);
      }

      const config = {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      };

      const response = await api.post<LoginResponse>(
        "/login/access-token",
        formData.toString(),
        config
      );
      return this.createUserSession(response.data, HOME_ROUTE);
    } catch (error) {
      let errorMessage = getApiErrorMessage(
        "Username and password do not match",
        error
      );
      throw new Error(errorMessage);
    }
  }

  /** Log out user by destroying the session and redirecting to login page */
  async logOut(request: Request) {
    const session = await getSession(request.headers.get("Cookie"));
    return redirect(LOGIN_ROUTE, {
      headers: {
        "Set-Cookie": await destroySession(session),
      },
    });
  }

  /** Sign up user */
  async signUp(user: CreateUser) {
    try {
      const response = await api.post<User>("/users", { ...user });
      return response.data;
    } catch (error) {
      let errorMessage = getApiErrorMessage(
        "Unable to create your account. Please try again.",
        error
      );
      throw new Error(errorMessage);
    }
  }

  /** Send reset password code */
  async sendResetPasswordCode(phone_number: string) {
    try {
      const response = await api.post<OtpVerificationResponse>(
        "/forget-password",
        {
          phone_number,
        }
      );
      return response.data;
    } catch (error) {
      let errorMessage = getApiErrorMessage(
        "Unable to create your account. Please try again.",
        error
      );
      throw new Error(errorMessage);
    }
  }

  /** Reset password */
  async resetPassword(data: {
    password: string;
    otp: string;
    phone_number: string;
  }) {
    try {
      await api.post<ResetPasswordResponse>("/reset-password", {
        data,
      });
      return redirect(LOGIN_ROUTE);
    } catch (error) {
      let errorMessage = getApiErrorMessage(
        "Unable to create your account. Please try again.",
        error
      );
      throw new Error(errorMessage);
    }
  }

  /** Send phone number verification code */
  async sendPhoneNumberVerificationCode(phone_number: string) {
    try {
      const response = await api.post<OtpVerificationResponse>(
        `/phone-verification/send`,
        { phone_number }
      );
      return response.data;
    } catch (error) {
      let errorMessage = getApiErrorMessage(
        "Unable to generate verification code. Please try again.",
        error
      );
      throw new Error(errorMessage);
    }
  }

  /** Verify user */
  async verifyUserPhoneNumber(data: PhoneNumberVerification) {
    try {
      const response = await api.post<LoginResponse>(
        "/phone-verification/verify",
        {
          ...data,
        }
      );
      return this.createUserSession(
        { user: response.data.user, access_token: response.data.access_token },
        HOME_ROUTE
      );
    } catch (error) {
      let errorMessage = getApiErrorMessage(
        "Unable to create your account. Please try again.",
        error
      );
      throw new Error(errorMessage);
    }
  }

  private async createUserSession(data: UserCookie, redirectTo: string) {
    const session = await getSession();
    session.set(USER_COOKIE, data);
    return redirect(redirectTo, {
      headers: {
        "Set-Cookie": await commitSession(session),
      },
    });
  }
}

export const iamService = new IamService();

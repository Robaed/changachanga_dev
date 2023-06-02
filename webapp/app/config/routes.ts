export const LOGIN_ROUTE = "/login";
export const LOGOUT_ROUTE = "/logout";
export const EMAIL_VERIFICATION_ROUTE = "/verify_email"
export const ACCOUNT_VERIFICATION_ROUTE = "/verify";
export const FORGOT_PASSWORD_ROUTE = "/forgot-password";
export const SIGN_UP_ROUTE = "/sign-up";

export const HOME_ROUTE = "/";
export const CHANNELS_ROUTE = "/channels";
export const ACTIVITIES_ROUTE = "/activities";

type MenuEntry = {
  label: string;
  href: string;
};
export const menuEntries: MenuEntry[] = [
  {
    label: "Home",
    href: HOME_ROUTE,
  },
  {
    label: "Channels",
    href: CHANNELS_ROUTE,
  },
  {
    label: "Activities",
    href: ACTIVITIES_ROUTE,
  },
];

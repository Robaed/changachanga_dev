import { createCookieSessionStorage } from "@remix-run/node";

const { getSession, commitSession, destroySession } =
  createCookieSessionStorage({
    cookie: {
      name: "__changachanga",
      // Expires can also be set (although maxAge overrides it when used in combination).
      // Note that this method is NOT recommended as `new Date` creates only one date on each server deployment, not a dynamic date in the future!
      //
      // expires: new Date(Date.now() + 60_000),
      httpOnly: process.env.NODE_ENV === "production",
      maxAge: 604_800,
      path: "/",
      sameSite: "lax",
      secrets: [String(process.env.SESSION_SECRET)],
      secure: process.env.NODE_ENV === "production",
    },
  });

export { getSession, commitSession, destroySession };

import { cssBundleHref } from "@remix-run/css-bundle";
import {
  json,
  LinksFunction,
  V2_MetaFunction as MetaFunction
} from "@remix-run/node";
import {
  Links,
  LiveReload,
  Meta,
  Outlet,
  Scripts,
  ScrollRestoration,
  useLoaderData
} from "@remix-run/react";
import { metaV1 } from "@remix-run/v1-meta";
import favicon from "~/assets/images/favicon.png";
import styles from "~/assets/styles/tailwind.css";

export const links: LinksFunction = () => [
  ...(cssBundleHref ? [{ rel: "stylesheet", href: cssBundleHref }] : []),
  { rel: "stylesheet", href: styles },
  {
    rel: "icon",
    href: favicon,
  },
];

export const meta: MetaFunction = (args) => {
  return metaV1(args, {
    title: "Changachanga",
  });
};

export async function loader() {
  return json({
    ENV: {
      SENTRY_DSN: process.env.SENTRY_DSN,
      NODE_ENV: process.env.NODE_ENV,
    },
  });
}

export default function App() {
  const data = useLoaderData<typeof loader>();
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width,initial-scale=1" />
        <Meta />
        <Links />
      </head>
      <body>
        <Outlet />
        <ScrollRestoration />
        <script
          dangerouslySetInnerHTML={{
            __html: `window.ENV = ${JSON.stringify(data.ENV)}`,
          }}
        />
        <Scripts />
        <LiveReload />
      </body>
    </html>
  );
}

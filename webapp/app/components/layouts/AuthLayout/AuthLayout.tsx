import React from "react";
import Logo from "~/assets/images/logo.svg";

import { TopAppBar } from "~/components/navigation";
import { FooterAppBar } from "~/components/navigation";

type Props = {
  title: string;
  children: React.ReactNode | React.ReactNode[];
};

/** Auth pages layout */
const AuthLayout: React.FC<Props> = ({ children, title }) => {

  return (
    <div className="w-full h-screen overflow-none">
      <TopAppBar />
      <div className="bg-secondary"></div>
      <div className="p-12 flex justify-center align-center">
        <div className="flex gap-12 ">
          {/* <div>
            <img
              src={Logo}
              alt="Changachanga logo"
              className="object-contain"
            />
          </div> */}
          <div className="flex flex-col gap-6">
            <p className="text-lg font-medium">{title}</p>
            {children}
          </div>
        </div>
      </div>
      <FooterAppBar />
    </div>
  );
};


export default AuthLayout;

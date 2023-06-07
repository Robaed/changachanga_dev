import React from "react";
import { TopAppBar } from "~/components/navigation";
import { FooterAppBar } from "~/components/navigation";

type Props = {
  children: React.ReactNode | React.ReactNode[];
};
export default function MainLayout({ children }: Props) {
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
            {children}
          </div>
        </div>
      </div>
      <FooterAppBar />
    </div>
  );
}

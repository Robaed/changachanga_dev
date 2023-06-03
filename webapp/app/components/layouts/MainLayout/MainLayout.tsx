import React from "react";
import { TopAppBar } from "~/components/navigation";
import { FooterAppBar } from "~/components/navigation";

type Props = {
  children: React.ReactNode | React.ReactNode[];
};
export default function MainLayout({ children }: Props) {
  return (
    <div className="">
      <TopAppBar />
      <div>
        <main className="">
          {children}
        </main>
      </div>
      <FooterAppBar />
    </div>
  );
}

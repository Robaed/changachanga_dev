import React from "react";
import { TopAppBar } from "~/components/navigation";

type Props = {
  children: React.ReactNode | React.ReactNode[];
};
export default function MainLayout({ children }: Props) {
  return (
    <div className="bg-gray-100">
      <TopAppBar />
      <div className="h-[calc(100vh_-_76px)]">
        <aside className="min-w-[256px] w-[256px] bg-secondary fixed h-[calc(100vh_-_76px)] mt-[76px] top-0"></aside>
        <main className="mt-[76px] ml-[256px] overflow-y-scroll w-[calc(100vw_-_256px)]">
          {children}
        </main>
      </div>
    </div>
  );
}

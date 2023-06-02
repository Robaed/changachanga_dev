import { NavLink } from "@remix-run/react";
import React from "react";
import Logo from "~/assets/images/logo.svg";
import { menuEntries } from "~/config/routes";

/** Top menu bar */
const TopAppBar: React.FC = () => {
  return (
    <nav className="main-header-nav w-full bg-white h-[76px] flex items-center fixed top-0">
      <div className="px-3 pl-16 bg-white">
        <img
          src={Logo}
          alt="Changachanga logo"
          className="w-full object-contain h-12"
        />
      </div>
      <div className="text-white h-full flex gap-6 items-center p-6 w-full">
        {/* {menuEntries.map((entry) => (
        //   <NavLink to={entry.href} key={entry.href}>
        //     {entry.label}
        //   </NavLink>
        ))} */}
      </div>
    </nav>
  );
};

export default TopAppBar;

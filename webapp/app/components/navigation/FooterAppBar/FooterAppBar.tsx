import { NavLink } from "@remix-run/react";
import React from "react";
import Logo from "~/assets/images/logo.svg";
import { menuEntries } from "~/config/routes";

/** Footer menu bar */
const FooterAppBar: React.FC = () => {
  return (
    <nav className="main-footer-nav w-full h-[76px] flex items-center bottom-0 grid mt-20 grid-cols-3">
      <div style={{ textAlign: "center", fontSize: "0.6rem", color: "white" }}>
        <span>© 2023 Changa Changa | Powered by KCB Group</span>
      </div>
      <div className="">
        <img
          src={Logo}
          alt="Changachanga logo"
          className="w-full object-contain h-12"
        />
        
      </div>
      <div style={{ textAlign: "center", fontSize: "0.65rem", color: "white" }}>
        <span>Social Media Disclaimer | Terms & Condition | Cookie Policy | Data Privacy Statement</span>
      </div>
    </nav>
  );
};

export default FooterAppBar;

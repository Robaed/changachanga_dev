import clsx from "clsx";
import React from "react";

type Props = {
  children: React.ReactNode;
  variant: "success" | "error" | "warning";
};

const Alert: React.FC<Props> = ({ children, variant }) => {
  return (
    <div
      className={clsx("p-2 text-sm rounded-md", {
        "bg-green-300 text-green-800": variant === "success",
        "bg-red-300 text-red-800": variant === "error",
        "bg-yellow-300 text-yellow-800": variant === "warning",
      })}
    >
      {children}
    </div>
  );
};

export default Alert;

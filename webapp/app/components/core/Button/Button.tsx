import clsx from "clsx";
import React from "react";

interface Props extends React.ComponentProps<"button"> {
  variant?: "solid" | "outline";
}

const Button: React.FC<Props> = ({
  className,
  children,
  variant = "solid",
  type = "button",
  ...props
}) => {
  return (
    <button
      type={type}
      className={clsx(
        "px-4 py-3 h-11 w-fit rounded-md text-sm flex gap-2 justify-center items-center",
        {
          "bg-[#00313D] text-white": variant === "solid",
          "bg-white text-gray-500 border border-gray-300":
            variant === "outline",
        },
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
};

export default Button;

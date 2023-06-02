import clsx from "clsx";
import React from "react";
import Label from "../Label/Label";

interface Props extends React.ComponentProps<"input"> {
  label?: string;
  error?: string;
  hint?: string;
}
const TextInput: React.FC<Props> = ({
  label,
  type = "text",
  className,
  error,
  hint,
  ...props
}) => {
  if (!type) {
    throw new Error("Please define a type for your input field");
  }
  return (
    <div className="grid gap-1">
      {label && (
        <Label label={label} htmlFor={props.id} required={props.required} />
      )}
      <input
        type={type}
        className={clsx(
          "bg-white text-black border-[#DCDCDC] focus:border-primary focus:ring-primary rounded-md p-2 h-11",
          className
        )}
        {...props}
      />
      {hint && <p className="text-sm text-primary">{hint}</p>}
      {error && <p className="text-sm text-red-400">{error}</p>}
    </div>
  );
};

export default TextInput;

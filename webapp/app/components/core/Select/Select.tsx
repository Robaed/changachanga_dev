import clsx from "clsx";
import React from "react";
import type { SelectOption } from "~/types";
import Label from "../Label/Label";

interface Props extends React.ComponentProps<"select"> {
  label: string;
  options: SelectOption[];
  error?: string;
  hint?: string;
}
const Select: React.FC<Props> = ({
  options,
  label,
  hint,
  error,
  className,
  ...props
}) => {
  return (
    <div className="grid gap-1 bg-white">
      {label && (
        <Label label={label} htmlFor={props.id} required={props.required} />
      )}
      <select
        className={clsx(
          "bg-white text-black border-[#DCDCDC] rounded-md focus:border-primary focus:ring-primary",
          className
        )}
        {...props}
      >
        {options.map((option) => (
          <option
            value={option.value}
            key={option.value}
            defaultValue={options[0].value}
          >
            {option.label}
          </option>
        ))}
      </select>
      {hint && <p className="text-sm text-primary">{hint}</p>}
      {error && <p className="text-sm text-red-400">{error}</p>}
    </div>
  );
};

export default Select;

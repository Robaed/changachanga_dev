import React from "react";

type Props = {
  htmlFor?: string;
  required?: boolean;
  label: string;
};
const Label: React.FC<Props> = ({ htmlFor, required, label }) => {
  return (
    <label htmlFor={htmlFor} className="text-sm text-[#444444]">
      {label} {required && "*"}
    </label>
  );
};

export default Label;

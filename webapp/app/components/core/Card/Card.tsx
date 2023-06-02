import React from "react";

type Props = {
  children: React.ReactNode | React.ReactNode[];
};
const Card: React.FC<Props> = ({ children }) => {
  return (
    <div className="bg-white p-4 rounded-md shadow-lg w-full">{children}</div>
  );
};

export default Card;

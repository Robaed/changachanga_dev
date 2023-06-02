import React from "react";

type Props = {};
const Channel: React.FC<Props> = () => {
  return (
    <div className="w-full border-4 border-transparent border-l-primary rounded-md shadow-lg py-2 px-3 flex items-center gap-3 justify-between">
      <div className="flex gap-2 items-center">
        <div>
          <p className="text-[#494949] text-sm font-medium">
            Michael Soandaso School Fees
          </p>
          <p className="text-[#767676] text-xs flex gap-1">
            <span>Created at: 06/05/2023</span>
            <span>ID: CHA12345#</span>
          </p>
        </div>
      </div>

      <div className="text-right">
        <p className="text-sm text-[#494949]">Goal</p>
        <p className="text-[#494949] text-sm">
          KES <span className="font-medium">100,000.00</span>
        </p>
      </div>
    </div>
  );
};

export default Channel;

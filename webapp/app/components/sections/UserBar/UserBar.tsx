import { Link } from "@remix-run/react";
import React from "react";
import { Button, TextInput } from "~/components/core";
import { HOME_ROUTE } from "~/config/routes";

const UserBar = () => {
  return (
    <div className="bg-white shadow-lg grid grid-cols-2 items-center gap-6 py-3 px-4">
      <div className="flex gap-3 items-center">
        <img
          src="https://via.placeholder.com/150"
          alt="user"
          className="rounded-full h-[75px] w-[75px] object-cover "
        />
        <div className="grid gap-1">
          <p className="text-lg text-[#00313D] font-bold">Jane Doe</p>
          <div className="flex gap-1 items-center">
            <p className="text-xs text-[#E04F5F]">Not verified</p>
            <Link to={HOME_ROUTE}>
              <button className="bg-[#FF3D00] bg-opacity-40 text-[#474747] text-xs px-2 py-[1px] rounded-md">
                Verify Now
              </button>
            </Link>
          </div>
        </div>
      </div>
      <div className="flex gap-3">
        <TextInput
          name="inviteCode"
          id="inviteCode"
          placeholder="Paste Changa Changa code here to join"
          className="w-fit-content"
        />
        <Button>Join Channel</Button>
      </div>
    </div>
  );
};

export default UserBar;

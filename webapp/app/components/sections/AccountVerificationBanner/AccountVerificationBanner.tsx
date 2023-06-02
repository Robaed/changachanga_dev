import { UserCircleIcon, XCircleIcon } from "@heroicons/react/24/outline";
import React from "react";
import { Card } from "~/components/core";

const AccountVerificationBanner = () => {
  return (
    <Card>
      <div className="grid gap-3">
        <div className="flex justify-between items-center">
          <UserCircleIcon className="h-4 w-4 text-red-400" />
          <button type="button">
            <XCircleIcon className="h-4 w-4 text-red-400" />
          </button>
        </div>

        <div>
          <p className="text-base text-[#444444]">
            Account verification is required
          </p>
          <p className="text-sm text-[#767676]">
            Verify your account to start creating channels
          </p>
        </div>
      </div>
    </Card>
  );
};

export default AccountVerificationBanner;

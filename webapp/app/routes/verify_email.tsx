import { Link } from "@remix-run/react";
import { Card } from "~/components/core";
import { MainLayout } from "~/components/layouts";
import {
  AccountVerificationBanner,
  Channel,
  UserBar,
} from "~/components/sections";
import { CHANNELS_ROUTE } from "~/config/routes";

export default function EmailVerification() {
  return (
    <MainLayout>
      <div className="grid gap-3">
        <UserBar />
        <div className="grid grid-cols-2 gap-3 px-3">
          
          <Card>
            <div className="grid grid-cols-3 divide-x">
              <div className="px-1">
                <p className="text-primary font-medium text-4xl">0</p>
                <p className="text-[#767676] text-sm">Joined Channels</p>
              </div>
              <div className="px-1">
                <p className="text-primary font-medium text-4xl">0</p>
                <p className="text-[#767676] text-sm">Active Participation</p>
              </div>
              <div className="px-1">
                <p className="text-primary font-medium text-4xl">0</p>
                <p className="text-[#767676] text-sm">Declined Requests</p>
              </div>
            </div>
          </Card>

          <Card>
            <div className="grid gap-3">
              <div className="flex justify-between items-center">
                <p className="text-sm text-[#444444]">
                  Your joined channels will appear here
                </p>
                <Link className="text-xs text-[#444444]" to={CHANNELS_ROUTE}>
                  View All
                </Link>
              </div>
              <div className="grid gap-3">
                <Channel />
                <Channel />
                <Channel />
              </div>
            </div>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
}

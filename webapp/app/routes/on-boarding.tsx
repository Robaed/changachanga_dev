import { MainLayout } from "~/components/layouts";
import { Alert, Button, Select, TextInput } from "~/components/core";

import OnboardingImage from "~/assets/images/on_boarding.png"

import { CHANNELS_ROUTE } from "~/config/routes";

export default function Onboarding() {
  return (
    <MainLayout>
      
    <div style={{ marginLeft : "30%", marginRight : "30%", marginTop: "16%;", marginBottom: "10%;" }} className="p-8 mt-10 bg-white border border-gray-200 rounded-lg shadow dark:bg-gray-800 dark:border-gray-700">

        <div className="flex justify-center">
            <img src={OnboardingImage} />
        </div>

        <div style={{ marginRight: "16%", marginLeft: "16%" }} className="content-center text-center">
            <p className="font-semibold text-center text-xl">Create your first channel</p>
            <p className="pt-5 text-sm font-light">A channel is an electronic account set up to receive payments related to a particular course</p>
        </div>

        <div className="flex mt-4 content-center justify-center">
            
        </div>

        <div className="flex mt-4 content-center justify-center">
            <Button type="submit">
                <span>Join Channel</span>
            </Button>
        </div>

        <div className="flex mt-4 content-center justify-center">
            <Button variant="outline">Vefify Account</Button>
        </div>

        


    </div>

    </MainLayout>
  );
}

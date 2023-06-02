import * as React from "react";
import * as RadixToast from "@radix-ui/react-toast";
import clsx from "clsx";

type Props = {
  label?: string;
  variant: "success" | "error" | "warning";
};
const Toast: React.FC<Props> = ({ label, variant }) => {
  const [open, setOpen] = React.useState(true);

  return (
    <RadixToast.Provider swipeDirection="right">
      <RadixToast.Root
        className={clsx(
          "rounded-md shadow-[hsl(206_22%_7%_/_35%)_0px_10px_38px_-10px,_hsl(206_22%_7%_/_20%)_0px_10px_20px_-15px] p-[15px] grid [grid-template-areas:_'title_action'_'description_action'] grid-cols-[auto_max-content] gap-x-[15px] items-center data-[state=open]:animate-slideIn data-[state=closed]:animate-hide data-[swipe=move]:translate-x-[var(--radix-toast-swipe-move-x)] data-[swipe=cancel]:translate-x-0 data-[swipe=cancel]:transition-[transform_200ms_ease-out] data-[swipe=end]:animate-swipeOut",
          {
            "bg-green-300 text-green-800": variant === "success",
            "bg-red-300 text-red-800": variant === "error",
            "bg-yellow-300 text-yellow-800": variant === "warning",
          }
        )}
        open={open}
        onOpenChange={setOpen}
        duration={5000}
      >
        {label && (
          <RadixToast.Title className="[grid-area:_title] mb-[5px] font-normal text-slate12 text-[15px]">
            {label}
          </RadixToast.Title>
        )}
      </RadixToast.Root>
      <RadixToast.Viewport className="[--viewport-padding:_25px] fixed bottom-0 right-0 flex flex-col p-[var(--viewport-padding)] gap-[10px] w-[390px] max-w-[100vw] m-0 list-none z-[2147483647] outline-none" />
    </RadixToast.Provider>
  );
};

export default Toast;

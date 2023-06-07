import React, { useState, useMemo } from 'react'
import { json, LoaderArgs, redirect } from '@remix-run/node'
import { Form, useActionData, useLoaderData, useTransition } from '@remix-run/react'
import { Alert, Button, Select, TextInput } from "~/components/core";
import { getSession, commitSession } from '~/session.server'
import qs from 'qs'

import { AuthLayout } from "~/components/layouts";

import DatePicker from 'react-date-picker';

import countryList from 'react-select-country-list';
// import { useSpinDelay } from 'spin-delay'
import clsx from 'clsx'


import PersonalInfoIcon from "~/assets/images/personal_info_icon.png";
import govermentIdIcon from "~/assets/images/government_id_icon.png";


export const loader = async ({ request }: LoaderArgs) => {
  const url = new URL(request.url)
  const page = Number(url.searchParams.get('page') ?? '1')
  const session = await getSession(request.headers.get('cookie'))

  if (page < 4) {
    const data = session.get(`form-data-page-${page}`) ?? {}
    return json({ page, data })
  } else {
    // final page so just collect all the data to render
    const data = {
      ...session.get(`form-data-page-1`),
      ...session.get(`form-data-page-2`),
      ...session.get(`form-data-page-3`),
    }
    return json({ page, data })
  }
}

export const action = async ({ request }: LoaderArgs) => {
  const text = await request.text()
  // use qs.parse to support multi-value values (by email checkbox list)
  const { page, action, ...data } = qs.parse(text)

  const session = await getSession(request.headers.get('cookie'))
  session.set(`form-data-page-${page}`, data)

  const nextPage = Number(page) + (action === 'next' ? 1 : -1)
  return redirect(`?page=${nextPage}`, {
    headers: {
      'set-cookie': await commitSession(session),
    },
  })
}

type ActionData = {
    formError?: string;
    fieldsError?: {
      username?: string;
      password?: string;
    };
};

export default function AccountVerification() {
//   const transition = useTransition()
//   const showSpinner = useSpinDelay(transition.state !== 'idle', {
//     delay: 200,
//     minDuration: 300,
//   })

  const loaderData = useLoaderData()
  const page = Number(loaderData.page)
  const data = loaderData.data
  const actionData = useActionData<ActionData>();

  const [value, setValue] = useState('')
  const [dateValue, onDateChange] = useState(new Date());

  const changeHandler = value => {
    setValue(value)
  }
  const options = useMemo(() => countryList().getData(), [])

  const gender_options = [
    { value: 'male', label: 'Male' },
    { value: 'female', label: 'Female' }
  ]


  return (
    <AuthLayout title=''>
        <div className="container">
        <Form method="post" className="space-y-8 divide-y divide-gray-200">
            <input name="page" type="hidden" value={page} />
            <div className="pt-5 flex justify-between">
            <div className="flex items-center gap-1">
                {/* <Spinner visible={showSpinner} /> */}
            </div>
            
            </div>
            <div className="bg-white border border-gray-200 rounded-lg shadow dark:bg-gray-800 dark:border-gray-700 pb-8">
            
            {page === 1 && (
                <div className="p-14 pt-4 mt-4">

                <div>
                <div style={{ marginRight: "20%", marginLeft: "20%", marginTop: "12%" }} className="content-center text-center">
                    <p className="font-semibold text-center text-xl">Let’s get you verified</p>
                    <p className="pt-5 text-sm font-light">Select your residency and follow the steps.</p>
                </div>

                    <Form className="grid gap-3" method="post">
                        <div>
                            {actionData?.formError && (
                            <Alert variant="error">{actionData.formError}</Alert>
                            )}
                                                                                                                                                                                                                                                                                                                                                                                         
                            <Select label='Residency' options={options} value={value} onChange={changeHandler} className='font-light text-sm'/>
                        </div>
                        <div>
                            <p className='font-light pt-4 text-xs'>Complete the following steps to verify your account in 7 minutes</p>
                        </div>
                        
                        <div className='flex mt-4'>
                            <img className='mr-4' src={PersonalInfoIcon}/>
                            <span className='text-sm'>Personal Information</span>
                        </div>

                        <div className='flex'>
                            <img className='mr-4' src={govermentIdIcon}/>
                            <span className='text-sm'>Government-Issued ID</span>
                        </div>

                    </Form>
                </div>
            
            </div>
            )}
            {page === 2 && (
                <div className="p-14 pt-4 mt-4">

                <div>
                    <Form className="grid gap-3" method="post">
                        <div>
                            {actionData?.formError && (
                            <Alert variant="error">{actionData.formError}</Alert>
                            )}
                            
                            <Select label='Residency' options={options} value={value} onChange={changeHandler} className='font-light text-sm'/>
                        </div>
                        
                        <div className='mt-4'>
                            <TextInput 
                                type='text' 
                                label='Legal name'
                                placeholder='First Name'
                            >
                                
                            </TextInput>

                            <TextInput 
                                type='text'
                                placeholder='Middle Name'   
                            >   
                            </TextInput>

                            <TextInput 
                                type='text'
                                placeholder='Last Name'   
                            >
                            </TextInput>
                        </div>

                        <div className='mt-1'>
                            <TextInput 
                                type='text' 
                                label='ID/Passport Number'
                                placeholder='National ID/ Passport number'
                            >   
                            </TextInput>
                        </div>
                        
                        {/* <DatePicker onChange={onDateChange} value={dateValue} /> */}

                        <Select label='Gender' options={gender_options}/>



                    </Form>
                </div>
            
            </div>
            )}
            {page === 3 && (
                <div className="divide-y divide-gray-200 pt-8 space-y-6 sm:pt-10 sm:space-y-5">
                <div>
                    <h3 className="text-lg leading-6 font-medium text-gray-900">
                    Notifications
                    </h3>
                    <p className="mt-1 max-w-2xl text-sm text-gray-500">
                    We'll always let you know about important changes, but you
                    pick what else you want to hear about.
                    </p>
                </div>
                <div className="space-y-6 sm:space-y-5 divide-y divide-gray-200">
                    <div className="pt-6 sm:pt-5">
                    <div role="group" aria-labelledby="label-email">
                        <div className="sm:grid sm:grid-cols-3 sm:gap-4 sm:items-baseline">
                        <div>
                            <div
                            className="text-base font-medium text-gray-900 sm:text-sm sm:text-gray-700"
                            id="label-email"
                            >
                            By Email
                            </div>
                        </div>
                        <div className="mt-4 sm:mt-0 sm:col-span-2">
                            <div className="max-w-lg space-y-4">
                            <div className="relative flex items-start">
                                <div className="flex items-center h-5">
                                <input
                                    id="comments"
                                    name="email"
                                    value="comments"
                                    defaultChecked={data.email?.includes(
                                    'comments',
                                    )}
                                    type="checkbox"
                                    className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                                />
                                </div>
                                <div className="ml-3 text-sm">
                                <label
                                    htmlFor="comments"
                                    className="font-medium text-gray-700"
                                >
                                    Comments
                                </label>
                                <p className="text-gray-500">
                                    Get notified when someones posts a comment on a
                                    posting.
                                </p>
                                </div>
                            </div>
                            <div>
                                <div className="relative flex items-start">
                                <div className="flex items-center h-5">
                                    <input
                                    id="candidates"
                                    name="email"
                                    value="candidates"
                                    defaultChecked={data.email?.includes(
                                        'candidates',
                                    )}
                                    type="checkbox"
                                    className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                                    />
                                </div>
                                <div className="ml-3 text-sm">
                                    <label
                                    htmlFor="candidates"
                                    className="font-medium text-gray-700"
                                    >
                                    Candidates
                                    </label>
                                    <p className="text-gray-500">
                                    Get notified when a candidate applies for a
                                    job.
                                    </p>
                                </div>
                                </div>
                            </div>
                            <div>
                                <div className="relative flex items-start">
                                <div className="flex items-center h-5">
                                    <input
                                    id="offers"
                                    name="email"
                                    value="offers"
                                    defaultChecked={data.email?.includes(
                                        'offers',
                                    )}
                                    type="checkbox"
                                    className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                                    />
                                </div>
                                <div className="ml-3 text-sm">
                                    <label
                                    htmlFor="offers"
                                    className="font-medium text-gray-700"
                                    >
                                    Offers
                                    </label>
                                    <p className="text-gray-500">
                                    Get notified when a candidate accepts or
                                    rejects an offer.
                                    </p>
                                </div>
                                </div>
                            </div>
                            </div>
                        </div>
                        </div>
                    </div>
                    </div>
                    <div className="pt-6 sm:pt-5">
                    <div role="group" aria-labelledby="label-notifications">
                        <div className="sm:grid sm:grid-cols-3 sm:gap-4 sm:items-baseline">
                        <div>
                            <div
                            className="text-base font-medium text-gray-900 sm:text-sm sm:text-gray-700"
                            id="label-notifications"
                            >
                            Push Notifications
                            </div>
                        </div>
                        <div className="sm:col-span-2">
                            <div className="max-w-lg">
                            <p className="text-sm text-gray-500">
                                These are delivered via SMS to your mobile phone.
                            </p>
                            <div className="mt-4 space-y-4">
                                <div className="flex items-center">
                                <input
                                    id="push-everything"
                                    name="pushNotifications"
                                    value="everything"
                                    defaultChecked={
                                    data.pushNotifications === 'everything'
                                    }
                                    type="radio"
                                    className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300"
                                />
                                <label
                                    htmlFor="push-everything"
                                    className="ml-3 block text-sm font-medium text-gray-700"
                                >
                                    Everything
                                </label>
                                </div>
                                <div className="flex items-center">
                                <input
                                    id="push-email"
                                    name="pushNotifications"
                                    value="email"
                                    defaultChecked={
                                    data.pushNotifications === 'email'
                                    }
                                    type="radio"
                                    className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300"
                                />
                                <label
                                    htmlFor="push-email"
                                    className="ml-3 block text-sm font-medium text-gray-700"
                                >
                                    Same as email
                                </label>
                                </div>
                                <div className="flex items-center">
                                <input
                                    id="push-nothing"
                                    name="pushNotifications"
                                    value="none"
                                    defaultChecked={
                                    data.pushNotifications === 'none'
                                    }
                                    type="radio"
                                    className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300"
                                />
                                <label
                                    htmlFor="push-nothing"
                                    className="ml-3 block text-sm font-medium text-gray-700"
                                >
                                    No push notifications
                                </label>
                                </div>
                            </div>
                            </div>
                        </div>
                        </div>
                    </div>
                    </div>
                </div>
                </div>
            )}
            {page === 4 && <pre>{JSON.stringify(data, null, 2)}</pre>}
            
            <div className="flex justify-center">
                {page > 1 && (
                <button
                    name="action"
                    value="previous"
                    formNoValidate
                    className="px-4 py-3 h-11 w-fit rounded-md text-sm flex gap-2 justify-center items-center bg-white text-gray-500 border border-gray-300 mr-4"
                >
                    Back
                </button>
                )}
                {page < 4 && (
                <button
                    name="action"
                    value="next"
                    className="px-4 py-3 h-11 w-fit rounded-md text-sm flex gap-2 justify-center items-center bg-[#00313D] text-white"
                >
                    Continue
                </button>
                )}
            </div>

            </div>

            
        </Form>
        </div>
    </AuthLayout>
  )
}

{/* function Spinner({ visible }: { visible: boolean }) {
  return (
    <SpinnerIcon
      className={clsx('animate-spin transition-opacity', {
        'opacity-0': !visible,
        'opacity-100': visible,
      })}
    />
  )
}

export function SpinnerIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg width={24} height={24} fill="none" {...props}>
      <path
        d="M12 4.75v1.5M17.127 6.873l-1.061 1.061M19.25 12h-1.5M17.127 17.127l-1.061-1.061M12 17.75v1.5M7.934 16.066l-1.06 1.06M6.25 12h-1.5M7.934 7.934l-1.06-1.06"
        stroke="currentColor"
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}
function setValue(value: any) {
    throw new Error('Function not implemented.');
} */}


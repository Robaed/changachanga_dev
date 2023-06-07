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
                
                <div className="p-14 pt-4 mt-4">
                    <div style={{ marginRight: "20%", marginLeft: "20%", marginTop: "12%" }} className="content-center text-center">
                        <p className="font-semibold text-center text-xl">Residential Address</p>
                        <p className="pt-5 text-sm font-light">Fill in your current Resdential Address.</p>
                    </div>
                    <div>
                        <Form className="grid gap-3" method="post">
                            <div>
                                {actionData?.formError && (
                                <Alert variant="error">{actionData.formError}</Alert>
                                )}
                                
                                {/* <Select label='Residential Address' options={options} value={value} onChange={changeHandler} className='font-light text-sm'/> */}
                                <div className='mt-4'>
                                    <TextInput
                                        label="Residential Address"
                                        placeholder="Street,Estate,House No/Door number"
                                    >
                                    </TextInput>
                                </div>
                                
                            </div>
                            
                            <div className='mt-4'>
                                <TextInput 
                                    type='text' 
                                    label='Postal Address'
                                    placeholder='Postal Adress'
                                >                                    
                                </TextInput>

                                <TextInput 
                                    type='text'
                                    label="Postal code"
                                    placeholder='Postal Code'   
                                >   
                                </TextInput>

                                <TextInput 
                                    type='text'
                                    label="City"
                                    placeholder='City'   
                                >
                                </TextInput>
                            </div>

                            <div className='mt-1'>
                                <TextInput 
                                    type='text' 
                                    label='Country/Region'
                                    placeholder='Country/Region'
                                >   
                                </TextInput>
                            </div>
                            <p className="h-0.5">Address must include all information (including any house Number/apartment number)</p>
                        </Form>
                    </div>
                </div>
            )}
            {page === 4 && (
                <div className="p-14 pt-4 mt-4">
                    <div style={{ marginRight: "20%", marginLeft: "20%", marginTop: "12%" }} className="content-center text-center">
                        <p className="font-semibold text-center text-xl">Let's get you verified</p>
                        <p className="pt-5 text-sm font-light">Select your residency and follow the steps</p>
                    </div>
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
                                    type='radio'
                                    label='Upload image'
                                    >
                                    </TextInput>
                                    <TextInput
                                    type='radio'
                                    label='Passport'
                                    >
                                    </TextInput>
                        </div>

                    </Form>
                </div>
            
            </div>
            )}
            {page === 5 && (
                <div className="p-14 pt-4 mt-4">
                    <div style={{ marginRight: "20%", marginLeft: "20%", marginTop: "12%" }} className="content-center text-center">
                        <p className="font-semibold text-center text-xl">Document verification</p>
                        <p className="pt-5 text-sm font-light">Take pictures of both side of your government issued  ID Card.</p>
                    </div>
                <div>
                    <Form className="grid gap-3" method="post">
                        <div>
                            {actionData?.formError && (
                            <Alert variant="error">{actionData.formError}</Alert>
                            )}
                            
                            {/* /<Select label='Residency' options={options} value={value} onChange={changeHandler} className='font-light text-sm'/> */}
                        </div>
                        <div className='mt-4'>
                                    <TextInput
                                        type='image'
                                        label='Upload image'
                                    >
                                    </TextInput>
                                    <ul>
                                        <li>
                                            Upload a complete image of your ID document.
                                        </li>
                                        <li>
                                            Ensure all details are readable.
                                        </li>
                                        <li>
                                            Ensure the document is the original & not expired.
                                        </li>
                                        <li>
                                            Place documents against a solid-colured background.
                                        </li>
                                    </ul>
                        </div>

                    </Form>
                </div>
            
            </div>
            )}
            {page === 6 && <pre>{JSON.stringify(data, null, 2)}</pre>}
            
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
                {page < 6 && (
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


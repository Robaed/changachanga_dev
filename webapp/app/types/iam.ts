export type User = {
  address_line: string;
  postal_code: string;
  city: string;
  country_code: "KE";
  full_name: string;
  id_number: string;
  gender: string;
  id_document_type: "NATIONAL_ID";
  id_date_of_issue: string;
  date_of_birth: string;
  first_name: string;
  middle_name: string;
  last_name: string;
  phone_number: string;
  email_address: string;
  account_no: number;
  date_joined_utc: string;
  is_active: string;
  is_superuser: string;
};

export type LoginResponse = {
  access_token: string;
  tokenType: string;
  user: User;
};

export type LoginDetails = {
  username: string;
  password: string;
};

export type UserCookie = {
  access_token: string;
  user: User;
};

export type CreateUser = Pick<
  User,
  | "address_line"
  | "country_code"
  | "full_name"
  | "id_number"
  | "id_document_type"
  | "date_of_birth"
  | "phone_number"
  | "gender"
  | "email_address"
  | "postal_code"
> & {
  nationality: string;
  password: string;
};

export type ResetPasswordResponse = {
  msg: string;
};

export type PhoneNumberVerification = {
  verification_code: string;
  phone_number: string;
};

export type OtpVerificationResponse = {
  status: number;
  message: string;
  detail: string;
};

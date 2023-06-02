export function validatePassword(password: string) {
  return password.length >= 6
    ? null
    : "Password should be at least 6 characters";
}

export function validatePhoneNumber(phoneNumber: string) {
  const pattern = "(254|0)(1|7)[0-9]{8}";
  const re = new RegExp(pattern);
  if (typeof phoneNumber !== "string" || !re.test(phoneNumber)) {
    return `Invalid phone number`;
  }
  return null;
}

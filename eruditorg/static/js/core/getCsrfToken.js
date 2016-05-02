import getCookie from './getCookie';


export default function getCsrfToken() {
  return getCookie('csrftoken');
};

import Commons from './Commons';
import Figures from './Figures';
import LoginModal from './Login';

const modules = {
  'Commons': new Commons(),
  'Figures': new Figures(),
  'LoginModal': new LoginModal()
};

export default modules;

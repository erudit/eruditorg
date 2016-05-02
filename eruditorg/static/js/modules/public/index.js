import Commons from './Commons';
import Figures from './Figures';
import LoginModal from './Login';
import Nav from './Nav';

const modules = {
  'Commons': new Commons(),
  'Figures': new Figures(),
  'LoginModal': new LoginModal(),
  'Nav': new Nav()
};

export default modules;

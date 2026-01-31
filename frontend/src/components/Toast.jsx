function Toast({ show, message, icon }) {
  return (
    <div className={`toast ${show ? 'show' : ''}`}>
      <span className="toast-icon">{icon}</span>
      <span className="toast-message">{message}</span>
    </div>
  );
}

export default Toast;

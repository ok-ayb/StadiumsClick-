function doThing(event) {
    event.preventDefault();
    window.confirm('test?') ? 
      window.location.href = '/delete' :
      null;
  };
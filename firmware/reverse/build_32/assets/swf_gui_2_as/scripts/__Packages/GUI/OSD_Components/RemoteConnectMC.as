class GUI.OSD_Components.RemoteConnectMC extends MovieClip
{
   var __mc;
   var __xmlSocket;
   var ARROWS_R;
   var ARROWS_L;
   var IP_A;
   var __cookie;
   var IP_B;
   var IP_C;
   var IP_D;
   var BTN_CAMERA;
   var BTN_STANDALONE;
   var __goFnc;
   var __intervalId;
   static var __cookieJar = "Sundance";
   function RemoteConnectMC(goFnc)
   {
      super();
      this.__mc = this;
      this.__xmlSocket = new XMLSocket();
      this.ARROWS_R._visible = false;
      this.ARROWS_L._visible = false;
      this.GetCookies();
      this.IP_A.text = this.__cookie.data.socAddr1;
      this.IP_B.text = this.__cookie.data.socAddr2;
      this.IP_C.text = this.__cookie.data.socAddr3;
      this.IP_D.text = this.__cookie.data.socAddr4;
      this.IP_A.restrict = "0-9";
      this.IP_B.restrict = "0-9";
      this.IP_C.restrict = "0-9";
      this.IP_D.restrict = "0-9";
      this.IP_A.maxChars = 3;
      this.IP_B.maxChars = 3;
      this.IP_C.maxChars = 3;
      this.IP_D.maxChars = 3;
      var _loc4_ = this;
      this.BTN_CAMERA.onPress = mx.utils.Delegate.create(this,this.CB_ButtonPress_CAMERA);
      this.BTN_STANDALONE.onPress = mx.utils.Delegate.create(this,this.CB_ButtonPress_STANDALONE);
      var _loc3_ = new Object();
      _loc3_.onChanged = mx.utils.Delegate.create(this,this.CB_TextField_Change);
      this.IP_A.addListener(_loc3_);
      this.IP_B.addListener(_loc3_);
      this.IP_C.addListener(_loc3_);
      this.IP_D.addListener(_loc3_);
      this.HandleChangeOfIP(true,500);
   }
   function CB_ButtonPress_CAMERA()
   {
      this.__goFnc(this.SocketAddress());
      this.CleanUp();
   }
   function CB_ButtonPress_STANDALONE()
   {
      this.__goFnc("");
      this.CleanUp();
   }
   function CB_TextField_Change(textfield_txt)
   {
      this.HandleChangeOfIP(false,150);
   }
   function CleanUp()
   {
      this.ARROWS_R.removeMovieClip();
      this.ARROWS_L.removeMovieClip();
      this.removeMovieClip();
   }
   function GetCookies()
   {
      this.__cookie = SharedObject.getLocal(GUI.OSD_Components.RemoteConnectMC.__cookieJar,"/");
      if(this.__cookie.data.socAddr1 == undefined)
      {
         this.__cookie.data.socAddr1 = "10";
      }
      if(this.__cookie.data.socAddr2 == undefined)
      {
         this.__cookie.data.socAddr2 = "3";
      }
      if(this.__cookie.data.socAddr3 == undefined)
      {
         this.__cookie.data.socAddr3 = "2";
      }
      if(this.__cookie.data.socAddr4 == undefined)
      {
         this.__cookie.data.socAddr4 = "1";
      }
      if(this.__cookie.data.socPort == undefined)
      {
         this.__cookie.data.socPort = "49152";
      }
      this.__cookie.data.flush();
   }
   function HandleChangeOfIP(checkAll, timeoutMS)
   {
      if(checkAll)
      {
         if(this.ForceValidIP())
         {
            this.AttemptConnect(timeoutMS);
         }
      }
      else
      {
         var tField = eval(Selection.getFocus());
         if(this.ForceValidIpField(tField))
         {
            this.AttemptConnect(timeoutMS);
         }
      }
   }
   function ForceValidIP()
   {
      var _loc2_ = this.ForceValidIpField(this.IP_A) && this.ForceValidIpField(this.IP_B) && this.ForceValidIpField(this.IP_C) && this.ForceValidIpField(this.IP_D);
      return _loc2_;
   }
   function ForceValidIpField(tField)
   {
      var _loc4_ = undefined;
      var _loc5_ = tField.text;
      var _loc2_ = Number(_loc5_);
      if(isNaN(_loc2_) || _loc2_ > 255 || _loc2_ < 1)
      {
         var _loc6_ = tField.text.length;
         Selection.setFocus(tField._name);
         Selection.setSelection(0,_loc6_);
         this.GoodConnection(false);
         _loc4_ = false;
      }
      else
      {
         tField.text = Math.round(_loc2_).toString();
         _loc4_ = true;
      }
      return _loc4_;
   }
   function CB_XmlSocketOnConnect(connectionStatus)
   {
      if(connectionStatus == true)
      {
         this.__cookie.data.socAddr1 = this.IP_A.text;
         this.__cookie.data.socAddr2 = this.IP_B.text;
         this.__cookie.data.socAddr3 = this.IP_C.text;
         this.__cookie.data.socAddr4 = this.IP_D.text;
         this.__cookie.data.socket = this.__xmlSocket;
         this.__cookie.data.flush();
         clearInterval(this.__intervalId);
         this.GoodConnection(true);
      }
      else
      {
         this.__cookie.data.socket = null;
         this.__cookie.data.flush();
         this.GoodConnection(false);
      }
   }
   function GoodConnection(good)
   {
      this.BTN_CAMERA._visible = good;
      this.ARROWS_R._visible = good;
      this.ARROWS_L._visible = good;
   }
   function AttemptConnect(timeoutMS)
   {
      function handleTimeout()
      {
         mc.__xmlSocket.close();
         clearInterval(this.__intervalId);
      }
      var mc = this;
      var _loc3_ = 1;
      var _loc2_ = 4;
      this.__xmlSocket.onConnect = mx.utils.Delegate.create(this,this.CB_XmlSocketOnConnect);
      this.__intervalId = setInterval(handleTimeout,timeoutMS);
      this.__xmlSocket.connect(this.SocketAddress(),this.SocketPort());
   }
   function EnableIpInput(enable)
   {
      this.IP_A.enable = enable;
      this.IP_B.enable = enable;
      this.IP_C.enable = enable;
      this.IP_D.enable = enable;
   }
   function SocketAddress()
   {
      var _loc2_ = this.IP_A.text + "." + this.IP_B.text + "." + this.IP_C.text + "." + this.IP_D.text;
      return _loc2_;
   }
   function SocketPort()
   {
      return 49152;
   }
}

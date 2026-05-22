class GUI.GPDB.GPdbXml extends XML
{
   var __state;
   var onLoad;
   var __gpdb;
   var STATE_PRE_REGISTRATION = 1;
   var STATE_REGISTRATION = 2;
   var STATE_POST_REG_PRE_INIT = 3;
   var STATE_INITIALIZATION = 4;
   var STATE_RUNNING = 5;
   function GPdbXml(gpdb)
   {
      super();
      _global.VxDebug("...........................................................................CTOR GPdbXml()");
      this.__state = this.STATE_PRE_REGISTRATION;
      this.ignoreWhite = true;
      this.onLoad = mx.utils.Delegate.create(this,this.CB_OnLoad);
      this.__gpdb = gpdb;
      mx.events.EventDispatcher.initialize(this);
   }
   function dispatchEvent()
   {
   }
   function addEventListener()
   {
   }
   function removeEventListener()
   {
   }
   function registerParams(pathname)
   {
   }
   function LoadDefaultsFromFile(pathname)
   {
      this.load(pathname);
   }
   function LoadDefaultsFromServer()
   {
   }
   function CB_OnLoad(success)
   {
      if(success)
      {
         this.loaded = true;
         this.parseSnippet();
         _root.gpdb.dump();
         var _loc3_ = {target:this,type:"EVENT_FACTORY_DEFAULTS_REGISTERED"};
         this.dispatchEvent(_loc3_);
      }
      throw new Error("ERROR! GPdbXml:CB_OnLoad(): Unable to load file: \'FactoryDefaults.xml\'");
   }
   function parseSnippet()
   {
      var _loc3_ = this.firstChild;
      while(_loc3_ != null)
      {
         switch(_loc3_.nodeName)
         {
            case "RedParameters":
               _loc3_ = _loc3_.firstChild;
               switch(this.__state)
               {
                  case this.STATE_PRE_REGISTRATION:
                     this.__state = this.STATE_REGISTRATION;
                     break;
                  case this.STATE_POST_REG_PRE_INIT:
                     this.__state = this.STATE_INITIALIZATION;
               }
               break;
            case "Cmnd":
               this.parseCmnd(_loc3_);
               _loc3_ = _loc3_.nextSibling;
               break;
            case "Param":
               this.parseParam(_loc3_);
               _loc3_ = _loc3_.nextSibling;
               break;
            case "Sync":
               this.parseSync(_loc3_);
            case "FactoryDefaults":
            case "FlashConfig":
            case "Profiles":
            case "Resource":
            case "DebugOverrides":
               _loc3_ = _loc3_.nextSibling;
               break;
            default:
               _global.VxError("GPdbXml.parseSnippet(): ERROR! Unknown node type \'" + this.nodeName + "\' " + this.Heritage(_loc3_));
               _loc3_ = _loc3_.nextSibling;
               break;
         }
      }
      switch(this.__state)
      {
         case this.STATE_REGISTRATION:
            this.__state = this.STATE_POST_REG_PRE_INIT;
            break;
         case this.STATE_INITIALIZATION:
            this.__state = this.STATE_RUNNING;
      }
   }
   function Heritage(node)
   {
      var _loc3_ = undefined;
      var _loc1_ = node;
      var _loc2_ = "";
      _loc3_ = 0;
      while(_loc1_ && _loc1_ != "null")
      {
         _loc2_ = "<" + _loc1_.nodeName + ">" + _loc2_;
         _loc1_ = _loc1_.parentNode;
      }
      return _loc2_;
   }
   function parseCmnd(node)
   {
      var _loc1_ = node.attributes.name;
      var _loc3_ = node.attributes.arg;
      if(_loc1_ != undefined)
      {
         if(_loc3_ != undefined)
         {
            GUI.OSD_Components.Authenticate.GetManager().HandleXML(_loc1_,_loc3_);
         }
      }
   }
   function parseParam(node)
   {
      var _loc3_ = node.attributes.name;
      var _loc6_ = node.attributes.type;
      var _loc5_ = node.attributes.value;
      if(_loc3_ != undefined)
      {
         if(_loc6_ != undefined)
         {
            if(this.__state == this.STATE_REGISTRATION)
            {
               this.__gpdb.paramRegister(_loc3_,_loc6_,_loc5_);
               var _loc2_ = node.firstChild;
               var _loc7_ = undefined;
               while(_loc2_ != null)
               {
                  switch(_loc2_.nodeName)
                  {
                     case "Flags":
                        this.ParseFlags(_loc3_,_loc2_);
                        break;
                     case "Constraints":
                        this.ParseConstraints(_loc3_,_loc2_);
                  }
                  _loc2_ = _loc2_.nextSibling;
               }
            }
            else if(this.__state == this.STATE_INITIALIZATION || this.__state == this.STATE_RUNNING)
            {
               this.__gpdb.paramSetLocal(_loc3_,_loc5_);
            }
         }
      }
   }
   function ParseFlags(paramName, parentNode)
   {
      var _loc4_ = parentNode.firstChild;
      var _loc7_ = this.__gpdb.getParam(paramName);
      while(_loc4_ != null)
      {
         var _loc3_ = _loc4_.nodeName;
         switch(_loc3_)
         {
            case "UI":
            case "Guicmd":
            case "Event":
            case "Capability":
            case "Security":
            case "Access":
               break;
            case "Profiled":
               if(paramName.indexOf("GUI.") == 0)
               {
                  var _loc6_ = _loc4_.attributes.type;
                  if(_loc6_.indexOf("system") == 0)
                  {
                     _global.VxDebug("GPdbXml.ParseFlags(): \'" + paramName + "\' is profiled as: \'" + _loc6_ + "\'");
                  }
               }
               break;
            default:
               _global.VxError("Warning! GPdbXml.ParseFlags(): Unrecognized flag! param: " + paramName + ", flag: \'" + _loc3_ + "\'");
               break;
         }
         _loc7_.addFlag(_loc3_);
         _loc4_ = _loc4_.nextSibling;
      }
   }
   function ParseConstraints(paramName, parentNode)
   {
      var _loc5_ = parentNode.firstChild;
      var _loc4_ = _global.gpdb.getParam(paramName);
      var _loc3_ = null;
      var _loc6_ = undefined;
      while(_loc5_ != null)
      {
         switch(_loc5_.nodeName)
         {
            case "Choices":
            case "LegalValues":
               _loc3_ = _loc5_.firstChild;
               while(_loc3_ != null)
               {
                  switch(_loc3_.nodeName)
                  {
                     case "Switch":
                        _loc4_.options.SetConditionalValues(this.ParseConditionalValues(_loc3_,_loc4_));
                        break;
                     case "Choice":
                        _loc4_.options.AddLegalValue({value:_loc3_.firstChild.nodeValue,label:_loc3_.attributes.UiTxt});
                        break;
                     case "Series":
                        _loc6_ = _loc3_.attributes.first.substr(0,1) == "+" || _loc3_.attributes.last.substr(0,1) == "+";
                        _loc4_.options.series = {start:Number(_loc3_.attributes.first),end:Number(_loc3_.attributes.last),increment:Number(_loc3_.attributes.increment),signed:_loc6_};
                        break;
                     case "LimitMaxParam":
                        _loc4_.options.SetMaxValueParam(_loc3_.attributes.param);
                        break;
                     case "DynamicallyGenerated":
                        _loc4_.options.SetOptionGeneratorParam(_loc3_.attributes.param);
                  }
                  _loc3_ = _loc3_.nextSibling;
               }
               break;
            case "Limits":
               break;
            case "StringLimits":
               break;
         }
         _loc5_ = _loc5_.nextSibling;
      }
   }
   function ParseConditionalValues(node, param)
   {
      var _loc13_ = [];
      var _loc14_ = node.attributes.param;
      var _loc12_ = undefined;
      var _loc6_ = undefined;
      var _loc4_ = node.firstChild;
      while(_loc4_ != null)
      {
         if(_loc4_.attributes.equals != null)
         {
            _loc12_ = GUI.GPDB.ConditionalValues.OPERATOR_EQUALS;
            _loc6_ = _loc4_.attributes.equals;
         }
         var _loc3_ = new GUI.GPDB.ConditionalValues(this.__gpdb,_loc14_,_loc12_,_loc6_,param);
         var _loc2_ = _loc4_.firstChild;
         while(_loc2_ != null)
         {
            if(_loc2_.nodeName == "Choice")
            {
               _loc3_.AddLegalValue({value:_loc2_.firstChild.nodeValue,label:_loc2_.attributes.UiTxt});
            }
            else if(_loc2_.nodeName == "Series")
            {
               var _loc5_ = _loc2_.attributes.first.substr(0,1) == "+" || _loc2_.attributes.last.substr(0,1) == "+";
               _loc3_.setSeries({start:Number(_loc2_.attributes.first),end:Number(_loc2_.attributes.last),increment:Number(_loc2_.attributes.increment),signed:_loc5_});
            }
            _loc2_ = _loc2_.nextSibling;
         }
         _loc13_.push(_loc3_);
         _loc4_ = _loc4_.nextSibling;
      }
      return _loc13_;
   }
   function parseSync(node)
   {
      var _loc3_ = node.attributes.id;
      if(_loc3_ == undefined)
      {
         _global.VxError("ERROR! PdbXml.parseSync(): SYNC with no ID");
      }
      else
      {
         var _loc4_ = {target:this,type:_loc3_};
         this.dispatchEvent(_loc4_);
      }
   }
}

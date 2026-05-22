class GUI.GPDB.ConditionalValues
{
   var __gpdb;
   var __paramName;
   var __operator;
   var __value;
   var __parentParam;
   var __optionSeries;
   var __optionValues;
   static var OPERATOR_EQUALS = 1;
   function ConditionalValues(gpdb, paramName, operator, value, parentParam)
   {
      this.__gpdb = gpdb;
      this.__paramName = paramName;
      this.__operator = operator;
      this.__value = value;
      this.__parentParam = parentParam;
      this.__gpdb.addCallbackWhenReady(paramName,mx.utils.Delegate.create(this,this.Update));
      this.__optionSeries = null;
      this.__optionValues = null;
   }
   function copy()
   {
      var _loc2_ = new GUI.GPDB.ConditionalValues(this.__gpdb,this.__paramName,this.__operator,this.__value,this.__parentParam);
      if(this.__optionSeries != undefined)
      {
         _loc2_.setSeries(this.__optionSeries.copy());
      }
      else
      {
         _loc2_.setSeries(undefined);
      }
      if(this.__optionValues != undefined)
      {
         _loc2_.setValues(this.__optionValues.copy());
      }
      else
      {
         _loc2_.setValues(undefined);
      }
      return _loc2_;
   }
   function Update(name, value)
   {
      if(name == this.__paramName && this.IsSatisfied())
      {
         var _loc4_ = undefined;
         if(this.__optionValues.list != null)
         {
            var _loc3_ = 0;
            while(_loc3_ < this.__optionValues.list.length)
            {
               if(this.__optionValues.list[_loc3_].value == this.__parentParam.value)
               {
                  return undefined;
               }
               _loc3_ = _loc3_ + 1;
            }
            _loc4_ = this.__optionValues.list[0].value;
         }
         if(this.__optionSeries != null)
         {
            if(this.__parentParam.value < this.__optionSeries.start)
            {
               _loc4_ = this.__optionSeries.start;
            }
            else if(this.__parentParam.value > this.__optionSeries.end)
            {
               _loc4_ = this.__optionSeries.end;
            }
            else
            {
               if((this.__parentParam.value - this.__optionSeries.start) % this.__optionSeries.increment == 0)
               {
                  return undefined;
               }
               _loc4_ = this.__optionSeries.start;
            }
         }
         _global.VxDebug("ConditionalValues::Update(" + name + ", " + value + ") set " + this.__parentParam.name + " = \'" + _loc4_ + "\'");
         this.__gpdb.paramSet(this.__parentParam.name,_loc4_);
      }
   }
   function AddLegalValue(itemObj)
   {
      if(this.__optionSeries)
      {
         throw new Error("ParamOptions:AddLegalValue(): a series has already been specified.");
      }
      var _loc5_ = false;
      if(this.__optionValues == undefined)
      {
         this.__optionValues = new Object();
         this.__optionValues.list = [];
         this.__optionValues.indexMap = [];
      }
      var _loc3_ = 0;
      while(_loc3_ < this.__optionValues.list.length)
      {
         if(this.__optionValues.list[_loc3_].value == itemObj.value)
         {
            return undefined;
         }
         _loc3_ = _loc3_ + 1;
      }
      itemObj.index = this.__optionValues.list.length;
      this.__optionValues.list.push(itemObj);
      this.__optionValues.indexMap[itemObj.value] = itemObj.index;
   }
   function setSeries(series)
   {
      this.__optionSeries = series;
   }
   function setValues(values)
   {
      this.__optionValues = values;
   }
   function getSeries()
   {
      return this.__optionSeries;
   }
   function getValues()
   {
      return this.__optionValues;
   }
   function IsSatisfied()
   {
      var _loc3_ = false;
      var _loc4_ = this.__gpdb.getParam(this.__paramName);
      var _loc5_ = _loc4_.options.GetExpandedChoice(_loc4_.value);
      var _loc0_ = null;
      if((_loc0_ = this.__operator) !== GUI.GPDB.ConditionalValues.OPERATOR_EQUALS)
      {
         _global.VxError("ConditionalValues:isSatisfied(): Unimplemented operator!");
      }
      else
      {
         _loc3_ = _loc5_ == this.__value;
      }
      return _loc3_;
   }
}

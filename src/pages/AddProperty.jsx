import { useState } from 'react'
import LocationPicker from '../components/LocationPicker';


function AddProperty() {
  const [step, setStep] = useState(1)
  const [dealType, setDealType] = useState('')
  const [basicInfo, setBasicInfo] = useState({
    title: '',
    description: '',
    property_type: '',
    area: '',
    rooms: '',
    floor: '',
    total_floors: '',
    build_year: '',
    direction: '',
    district: '',
    address: '',
    location: {
      lat: null,
      lng: null
  },
    // امکانات
    parking: false,
    elevator: false,
    storage: false,
    balcony: false,
    gym: false,
    pool: false,
    security: false,
    renovation: false,
  });
  const [saleInfo, setSaleInfo] = useState({
    document_type: '',
    total_price: '',
    price_per_meter: '',
    is_exchangeable: false,
    exchange_description: '',
    is_negotiable: false
  });
  const [rentInfo, setRentInfo] = useState({
    monthly_rent: '',
    deposit: '',
    is_convertible: false,
    minimum_lease: 12,
    has_transfer_fee: true
  });
  const [dailyRentInfo, setDailyRentInfo] = useState({
    daily_price: '',
    min_stay: 1,
    maximum_days: '',
    max_guests: 2,
    extra_person_fee: '',
    check_in_time: '14:00',
    check_out_time: '12:00'
  });

  // تست تغییر نوع معامله - اضافه کردن قبل از dealTypes
  const handleDealTypeChange = (type) => {
    console.log('Deal type changed to:', type);
    setDealType(type);
  };

  // تست تغییر موقعیت - اضافه کردن قبل از dealTypes
  const handleLocationSelect = (location) => {
    setBasicInfo(prev => ({
        ...prev,
        location: location
    }));
};

  const dealTypes = [
    {
      id: 'sale',
      title: 'فروش ملک',
      description: 'ثبت آگهی فروش ملک با جزئیات کامل',
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>
      )
    },
    {
      id: 'rent',
      title: 'اجاره ملک',
      description: 'ثبت آگهی اجاره با شرایط و ودیعه',
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
      )
    },
    {
      id: 'daily',
      title: 'اجاره روزانه',
      description: 'ثبت آگهی اجاره روزانه و کوتاه مدت',
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      )
    }
  ]
  
  // کامپوننت فرم اطلاعات پایه
  const BasicInfoForm = () => (
    <div className="space-y-6">
      {/* اطلاعات اصلی */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">عنوان آگهی</label>
                <input
                  type="text"
                  value={basicInfo.title}
                  onChange={(e) => setBasicInfo({...basicInfo, title: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">نوع ملک</label>
              <select
                value={basicInfo.property_type}
                onChange={(e) => setBasicInfo({...basicInfo, property_type: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">انتخاب کنید</option>
                <option value="apartment">آپارتمان</option>
                <option value="villa">ویلا</option>
                <option value="office">دفتر کار</option>
                <option value="store">مغازه</option>
                <option value="land">زمین</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">متراژ</label>
              <input
                type="number"
                value={basicInfo.area}
                onChange={(e) => setBasicInfo({...basicInfo, area: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">تعداد اتاق</label>
              <input
                type="number"
                value={basicInfo.rooms}
                onChange={(e) => setBasicInfo({...basicInfo, rooms: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">طبقه</label>
              <input
                type="number"
                value={basicInfo.floor}
                onChange={(e) => setBasicInfo({...basicInfo, floor: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">تعداد کل طبقات</label>
              <input
                type="number"
                value={basicInfo.total_floors}
                onChange={(e) => setBasicInfo({...basicInfo, total_floors: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
      </div>

      {/* توضیحات */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">توضیحات</label>
        <textarea
          value={basicInfo.description}
          onChange={(e) => setBasicInfo({...basicInfo, description: e.target.value})}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      {/* امکانات */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-3">امکانات</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { id: 'parking', label: 'پارکینگ' },
            { id: 'elevator', label: 'آسانسور' },
            { id: 'storage', label: 'انباری' },
            { id: 'balcony', label: 'بالکن' },
            { id: 'gym', label: 'سالن ورزشی' },
            { id: 'pool', label: 'استخر' },
            { id: 'security', label: 'نگهبانی' },
            { id: 'renovation', label: 'بازسازی شده' },
          ].map((feature) => (
            <label key={feature.id} className="flex items-center space-x-2 rtl:space-x-reverse">
              <input
                type="checkbox"
                checked={basicInfo[feature.id]}
                onChange={(e) => setBasicInfo({...basicInfo, [feature.id]: e.target.checked})}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">{feature.label}</span>
            </label>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-3">موقعیت مکانی</h3>
        <LocationPicker
            onLocationSelect={(location) => {
                setBasicInfo(prev => ({
                    ...prev,
                    location: {
                        lat: location.lat,
                        lng: location.lng
                    }
                }));
                // اضافه کردن اعتبارسنجی موقعیت
                if (location.lat && location.lng) {
                    setErrors(prev => ({
                        ...prev,
                        location: null
                    }));
                }
            }}
            initialLocation={
                basicInfo.location && basicInfo.location.lat && basicInfo.location.lng
                    ? basicInfo.location
                    : null
            }
            dealType={dealType}
        />
        {/* نمایش خطا اگر موقعیت انتخاب نشده باشد */}
        {errors?.location && (
            <p className="text-red-500 text-sm mt-1">{errors.location}</p>
        )}



          {basicInfo.location.lat && (
              <p className="text-sm text-gray-600 mt-2">
                  موقعیت انتخاب شده: طول جغرافیایی {basicInfo.location.lng.toFixed(6)}، عرض جغرافیایی {basicInfo.location.lat.toFixed(6)}
              </p>
          )}
      </div>

      {/* دکمه‌های پیمایش */}
      <div className="flex justify-between">
        <button
          onClick={() => setStep(1)}
          className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          مرحله قبل
        </button>
        <button
          onClick={() => setStep(3)}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          مرحله بعد
        </button>
      </div>
    </div>
  );
  const SalePropertyForm = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* نوع سند */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">نوع سند</label>
          <input
            type="text"
            value={saleInfo.document_type}
            onChange={(e) => setSaleInfo({...saleInfo, document_type: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="مثال: سند شش دانگ"
          />
        </div>
  
        {/* قیمت کل */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">قیمت کل (تومان)</label>
          <input
            type="number"
            value={saleInfo.total_price}
            onChange={(e) => setSaleInfo({...saleInfo, total_price: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="مثال: 1000000000"
          />
        </div>
  
        {/* قیمت هر متر */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">قیمت هر متر (تومان)</label>
          <input
            type="number"
            value={saleInfo.price_per_meter}
            onChange={(e) => setSaleInfo({...saleInfo, price_per_meter: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="مثال: 50000000"
          />
        </div>
      </div>
  
      {/* گزینه‌های اضافی */}
      <div className="space-y-4">
        <div className="flex items-center space-x-3 rtl:space-x-reverse">
          <input
            type="checkbox"
            id="is_exchangeable"
            checked={saleInfo.is_exchangeable}
            onChange={(e) => setSaleInfo({...saleInfo, is_exchangeable: e.target.checked})}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <label htmlFor="is_exchangeable" className="text-sm text-gray-700">قابل معاوضه</label>
        </div>
  
        {saleInfo.is_exchangeable && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">توضیحات معاوضه</label>
            <textarea
              value={saleInfo.exchange_description}
              onChange={(e) => setSaleInfo({...saleInfo, exchange_description: e.target.value})}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="شرایط معاوضه را شرح دهید..."
            />
          </div>
        )}
  
        <div className="flex items-center space-x-3 rtl:space-x-reverse">
          <input
            type="checkbox"
            id="is_negotiable"
            checked={saleInfo.is_negotiable}
            onChange={(e) => setSaleInfo({...saleInfo, is_negotiable: e.target.checked})}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <label htmlFor="is_negotiable" className="text-sm text-gray-700">قابل مذاکره</label>
        </div>
      </div>
  
      {/* دکمه‌های پیمایش */}
      <div className="flex justify-between mt-6">
        <button
          onClick={() => setStep(2)}
          className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          مرحله قبل
        </button>
        <button
          onClick={() => setStep(4)}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          مرحله بعد
        </button>
      </div>
    </div>
  );  

  const RentPropertyForm = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* ودیعه */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">ودیعه (تومان)</label>
          <input
            type="number"
            value={rentInfo.deposit}
            onChange={(e) => setRentInfo({...rentInfo, deposit: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="مثال: 100000000"
          />
        </div>
  
        {/* اجاره ماهیانه */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">اجاره ماهیانه (تومان)</label>
          <input
            type="number"
            value={rentInfo.monthly_rent}
            onChange={(e) => setRentInfo({...rentInfo, monthly_rent: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="مثال: 5000000"
          />
        </div>
  
        {/* حداقل مدت اجاره */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">حداقل مدت اجاره (ماه)</label>
          <input
            type="number"
            value={rentInfo.minimum_lease}
            onChange={(e) => setRentInfo({...rentInfo, minimum_lease: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            min="1"
          />
        </div>
      </div>
  
      {/* گزینه‌های اضافی */}
      <div className="space-y-4">
        <div className="flex items-center space-x-3 rtl:space-x-reverse">
          <input
            type="checkbox"
            id="is_convertible"
            checked={rentInfo.is_convertible}
            onChange={(e) => setRentInfo({...rentInfo, is_convertible: e.target.checked})}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <label htmlFor="is_convertible" className="text-sm text-gray-700">قابل تبدیل</label>
        </div>
  
        <div className="flex items-center space-x-3 rtl:space-x-reverse">
          <input
            type="checkbox"
            id="has_transfer_fee"
            checked={rentInfo.has_transfer_fee}
            onChange={(e) => setRentInfo({...rentInfo, has_transfer_fee: e.target.checked})}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <label htmlFor="has_transfer_fee" className="text-sm text-gray-700">کمیسیون دارد</label>
        </div>
      </div>
  
      {/* دکمه‌های پیمایش */}
      <div className="flex justify-between mt-6">
        <button
          onClick={() => setStep(2)}
          className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          مرحله قبل
        </button>
        <button
          onClick={() => setStep(4)}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          مرحله بعد
        </button>
      </div>
    </div>
  );

  const DailyRentPropertyForm = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* قیمت روزانه */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">قیمت روزانه (تومان)</label>
          <input
            type="number"
            value={dailyRentInfo.daily_price}
            onChange={(e) => setDailyRentInfo({...dailyRentInfo, daily_price: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="مثال: 1000000"
          />
        </div>
  
        {/* حداقل مدت اقامت */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">حداقل مدت اقامت (شب)</label>
          <input
            type="number"
            value={dailyRentInfo.min_stay}
            onChange={(e) => setDailyRentInfo({...dailyRentInfo, min_stay: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            min="1"
          />
        </div>
  
        {/* حداکثر مدت اقامت */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">حداکثر مدت اقامت (شب)</label>
          <input
            type="number"
            value={dailyRentInfo.maximum_days}
            onChange={(e) => setDailyRentInfo({...dailyRentInfo, maximum_days: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
  
        {/* حداکثر تعداد مهمان */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">حداکثر تعداد مهمان</label>
          <input
            type="number"
            value={dailyRentInfo.max_guests}
            onChange={(e) => setDailyRentInfo({...dailyRentInfo, max_guests: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            min="1"
          />
        </div>
  
        {/* هزینه نفر اضافه */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">هزینه نفر اضافه (تومان)</label>
          <input
            type="number"
            value={dailyRentInfo.extra_person_fee}
            onChange={(e) => setDailyRentInfo({...dailyRentInfo, extra_person_fee: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="مثال: 200000"
          />
        </div>
  
        {/* ساعت ورود و خروج */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">ساعت ورود</label>
          <input
            type="time"
            value={dailyRentInfo.check_in_time}
            onChange={(e) => setDailyRentInfo({...dailyRentInfo, check_in_time: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
  
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">ساعت خروج</label>
          <input
            type="time"
            value={dailyRentInfo.check_out_time}
            onChange={(e) => setDailyRentInfo({...dailyRentInfo, check_out_time: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>
  
      {/* دکمه‌های پیمایش */}
      <div className="flex justify-between mt-6">
        <button
          onClick={() => setStep(2)}
          className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          مرحله قبل
        </button>
        <button
          onClick={() => setStep(4)}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          مرحله بعد
        </button>
      </div>
    </div>
  );
  

  return (
    <div className="max-w-4xl mx-auto" dir="rtl">
        <h1 className="text-3xl font-bold text-center mb-8">ثبت آگهی جدید</h1>
        
        <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">نوع معامله را انتخاب کنید</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {dealTypes.map((type) => (
                  <button
                      key={type.id}
                      onClick={() => handleDealTypeChange(type.id)}
                      className={`p-4 rounded-lg border-2 transition-all duration-200 text-right
                        ${dealType === type.id 
                          ? 'border-blue-500 bg-blue-50' 
                          : 'border-gray-200 hover:border-blue-200'
                        }`}
                    >
                      <div className="text-blue-600 mb-3">{type.icon}</div>
                      <h3 className="font-semibold text-lg mb-2">{type.title}</h3>
                      <p className="text-gray-600 text-sm">{type.description}</p>
                  </button>
                ))}
            </div>

              {dealType && (
                <div className="mt-6 flex justify-end">
                    <button
                      onClick={() => setStep(2)}
                      className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      مرحله بعد
                    </button>
                </div>
            )}
        </div>
        {step === 2 && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-6">اطلاعات پایه ملک</h2>
            <BasicInfoForm />
          </div>
        )}
        {step === 3 && dealType === 'sale' && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-6">اطلاعات تخصصی ملک فروشی</h2>
            <SalePropertyForm />
          </div>
        )}
        {step === 3 && dealType === 'rent' && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-6">اطلاعات تخصصی ملک اجاره‌ای</h2>
            <RentPropertyForm />
          </div>
        )}
        {step === 3 && dealType === 'daily' && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-6">اطلاعات تخصصی اجاره روزانه</h2>
            <DailyRentPropertyForm />
          </div>
        )}



    </div>
  )
}

export default AddProperty

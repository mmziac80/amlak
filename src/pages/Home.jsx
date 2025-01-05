import PropertyCard from '../components/PropertyCard'
function Home() {
    // داده‌های نمونه - بعداً از API دریافت می‌شود
    const featuredProperties = {
        forSale: [
        { id: 1, title: "آپارتمان لوکس", location: "سعادت آباد", price: "2,500,000,000 تومان", type: "فروش", image: "/path/to/image" },
        // 4 مورد دیگر
        ],
        forRent: [
        { id: 1, title: "سوئیت اداری", location: "ونک", price: "15,000,000 تومان", type: "اجاره", image: "/path/to/image" },
        // 4 مورد دیگر
        ],
        daily: [
        { id: 1, title: "ویلای ساحلی", location: "رامسر", price: "2,000,000 تومان", type: "اجاره روزانه", image: "/path/to/image" },
        // 4 مورد دیگر
        ]
    }

    return (
      <div>
        {/* Hero Section */}
        <div className="relative overflow-hidden bg-gradient-to-b from-primary-900/50 to-black/50 py-20">
          <div className="container mx-auto px-4">
            <div className="text-center">
              <h1 className="font-display text-5xl font-bold mb-6 text-transparent bg-clip-text bg-gradient-to-r from-primary-300 to-secondary">
                سریع‌ترین راه برای یافتن خانه رویایی
              </h1>
              <p className="font-sans text-xl text-gray-300 mb-8">
                با پیشرفته‌ترین سیستم جستجو، ملک مورد نظر خود را پیدا کنید
              </p>
              
              {/* Search Box */}
              <div className="max-w-3xl mx-auto bg-white/10 backdrop-blur-lg rounded-lg p-4">
                <div className="flex gap-4">
                  <input 
                    type="text" 
                    placeholder="جستجوی ملک..."
                    className="font-sans flex-1 bg-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 outline-none focus:ring-2 focus:ring-primary-500"
                  />
                  <button className="bg-gradient-to-r from-primary-500 to-secondary text-white px-8 py-3 rounded-lg hover:opacity-90 transition-opacity font-sans">
                    جستجو
                  </button>
                </div>
              </div>
            </div>
          </div>
  
          {/* Background Effect */}
          <div className="absolute inset-0 -z-10">
            <div className="absolute inset-0 bg-gradient-to-r from-primary-900/20 to-secondary/20" />
          </div>
        </div>
        {/* Featured Properties Section */}
        <section className="py-16 bg-gradient-to-b from-gray-900 to-primary-900" dir="rtl">
            <div className="container mx-auto px-4">
                <h2 className="font-display text-3xl font-bold text-center mb-12 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
                    
                    {/* املاک فروشی */}
                    <div className="mb-12">
                        <h3 className="font-display text-2xl mb-6 text-primary-800">املاک فروشی برتر</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 rtl:grid-flow-row-dense">
                            {featuredProperties.forSale.map(property => (
                                <PropertyCard key={property.id} property={property} />
                            ))}
                        </div>
                    </div>

                    {/* املاک اجاره‌ای */}
                    <div className="mb-12">
                        <h3 className="font-display text-2xl mb-6 text-primary-800">املاک اجاره‌ای برتر</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 rtl:grid-flow-row-dense">
                            {featuredProperties.forRent.map(property => (
                                <PropertyCard key={property.id} property={property} />
                            ))}
                        </div>
                    </div>

                    {/* املاک اجاره روزانه */}
                    <div>
                        <h3 className="font-display text-2xl mb-6 text-primary-800">اجاره روزانه برتر</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 rtl:grid-flow-row-dense">
                            {featuredProperties.daily.map(property => (
                                <PropertyCard key={property.id} property={property} />
                            ))}
                        </div>
                    </div>
                </h2>
            </div>
        </section>
        {/* Why Choose Us Section */}
        <section className="py-16 bg-gradient-to-t from-gray-900 to-primary-900" dir="rtl">
            <div className="container mx-auto px-4">
                <h2 className="font-display text-3xl font-bold text-center mb-12 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
                    چرا املاک دیجیتال؟
                </h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                    {/* مزیت 1 */}
                    <div className="text-center p-6 bg-white/10 backdrop-blur-lg rounded-xl hover:bg-white/20 transition-all duration-300">
                       <div className="w-16 h-16 mx-auto mb-4 bg-primary-500/20 rounded-full flex items-center justify-center">
                            <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                        </div>
                        <h3 className="font-display text-xl font-bold mb-2 text-white">جستجوی سریع</h3>
                        <p className="text-gray-300">پیدا کردن ملک مناسب در کمترین زمان</p>
                    </div>

                    {/* مزیت 2 */}
                    <div className="text-center p-6 bg-white/10 backdrop-blur-lg rounded-xl hover:bg-white/20 transition-all duration-300">
                        <div className="w-16 h-16 mx-auto mb-4 bg-primary-500/20 rounded-full flex items-center justify-center">
                            <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                            </svg>
                        </div>
                        <h3 className="font-display text-xl font-bold mb-2 text-white">معاملات امن</h3>
                        <p className="text-gray-300">تضمین امنیت در تمام مراحل معامله</p>
                    </div>

                    {/* مزیت 3 */}
                    <div className="text-center p-6 bg-white/10 backdrop-blur-lg rounded-xl hover:bg-white/20 transition-all duration-300">
                        <div className="w-16 h-16 mx-auto mb-4 bg-primary-500/20 rounded-full flex items-center justify-center">
                            <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                            </svg>
                        </div>
                        <h3 className="font-display text-xl font-bold mb-2 text-white">مشاوران حرفه‌ای</h3>
                        <p className="text-gray-300">پشتیبانی توسط متخصصان املاک</p>
                    </div>

                    {/* مزیت 4 */}
                    <div className="text-center p-6 bg-white/10 backdrop-blur-lg rounded-xl hover:bg-white/20 transition-all duration-300">
                        <div className="w-16 h-16 mx-auto mb-4 bg-primary-500/20 rounded-full flex items-center justify-center">
                            <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                        </div>
                        <h3 className="font-display text-xl font-bold mb-2 text-white">صرفه‌جویی در زمان</h3>
                        <p className="text-gray-300">بازدید آنلاین و مقایسه سریع املاک</p>
                    </div>
                </div>
            </div>
        </section>
      </div>
    )
  }
  
  export default Home
  
"use client";

import React from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Calendar, 
  MapPin, 
  Users, 
  Heart, 
  ExternalLink,
  Sparkles,
  Clock,
  Euro,
  Star,
  Palette,
  Smile,
  Camera
} from "lucide-react";

export default function Home() {
  const [selectedImage, setSelectedImage] = React.useState(null);
  
  const scrollToSection = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };

  const images = [
    {
      url: "https://qtrypzzcjebvfcihiynt.supabase.co/storage/v1/object/public/base44-prod/public/68e796544654cada1ecae944/d1d8a6bb0_557036107_17995394777830538_6544187064721393763_n.jpg",
      alt: "Діти показують свої творчі роботи"
    },
    {
      url: "https://qtrypzzcjebvfcihiynt.supabase.co/storage/v1/object/public/base44-prod/public/68e796544654cada1ecae944/633a5d1f8_560678651_17996197403830538_6008668098288507872_n.jpg",
      alt: "Юрій з учасницею клубу"
    },
    {
      url: "https://qtrypzzcjebvfcihiynt.supabase.co/storage/v1/object/public/base44-prod/public/68e796544654cada1ecae944/f543cf1aa_IMG_7260.jpg",
      alt: "Веселі моменти на заняттях"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-yellow-100 via-pink-50 to-blue-100 relative overflow-hidden">
      {/* Floating decorations */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-20 left-10 w-16 h-16 bg-yellow-400 rounded-full opacity-20 animate-bounce" style={{animationDelay: '0s', animationDuration: '3s'}} />
        <div className="absolute top-40 right-20 w-12 h-12 bg-pink-400 rounded-full opacity-20 animate-bounce" style={{animationDelay: '1s', animationDuration: '4s'}} />
        <div className="absolute bottom-32 left-1/4 w-20 h-20 bg-blue-400 rounded-full opacity-20 animate-bounce" style={{animationDelay: '2s', animationDuration: '5s'}} />
        <div className="absolute top-1/2 right-10 w-14 h-14 bg-orange-400 rounded-full opacity-20 animate-bounce" style={{animationDelay: '1.5s', animationDuration: '3.5s'}} />
      </div>

      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-xl border-b-4 border-orange-400 shadow-2xl">
        <div className="container mx-auto px-4 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-3xl overflow-hidden shadow-2xl ring-4 ring-orange-300 transform hover:scale-110 transition-transform">
                <img 
                  src="https://qtrypzzcjebvfcihiynt.supabase.co/storage/v1/object/public/base44-prod/public/68e796544654cada1ecae944/0d0d3cd24_Screenshot2025-10-09at133431.png"
                  alt="Oekrainse Kids Club Logo"
                  className="w-full h-full object-cover"
                />
              </div>
              <div>
                <h1 className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-orange-500 via-pink-500 to-blue-500">
                  KIDS CLUB
                </h1>
                <p className="text-base font-bold text-orange-600">з Юрієм та Мариною</p>
              </div>
            </div>
            <Button
              onClick={() => window.open('https://forms.gle/Kr6mACYApcXdXt6S7', '_blank')}
              className="bg-gradient-to-r from-orange-500 to-pink-500 hover:from-orange-600 hover:to-pink-600 text-white font-bold text-lg px-8 py-6 rounded-3xl shadow-2xl transform hover:scale-105 transition-all"
            >
              <Star className="w-5 h-5 mr-2 animate-spin" style={{animationDuration: '3s'}} />
              Приєднатись
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative py-20 overflow-hidden">
        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-5xl mx-auto text-center">
            <h2 className="text-6xl md:text-7xl font-black mb-8 leading-tight">
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-500 via-pink-500 to-blue-500">
                Творчість
              </span>
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500">
                Дружба
              </span>
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-pink-500 via-orange-500 to-yellow-500">
                Радість
              </span>
            </h2>
            
            <p className="text-2xl text-gray-700 mb-10 leading-relaxed font-semibold">
              Український дитячий клуб творчості в Амстердамі<br />
              Діти розвивають креативність, спілкуються та зустрічають нових друзів
            </p>
            
            <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
              <Button
                size="lg"
                onClick={() => window.open('https://forms.gle/Kr6mACYApcXdXt6S7', '_blank')}
                className="bg-gradient-to-r from-pink-500 via-orange-500 to-yellow-500 hover:from-pink-600 hover:to-yellow-600 text-white font-black text-2xl px-12 py-8 rounded-3xl shadow-2xl transform hover:scale-110 transition-all w-full sm:w-auto"
              >
                <Sparkles className="w-6 h-6 mr-3" />
                Зареєструватись
              </Button>
              <Button
                size="lg"
                variant="outline"
                onClick={() => scrollToSection('details')}
                className="text-2xl px-12 py-8 rounded-3xl border-4 border-blue-500 font-black text-blue-600 hover:bg-blue-500 hover:text-white w-full sm:w-auto transform hover:scale-105 transition-all"
              >
                Дізнатись більше
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Fun Cards */}
      <section className="py-20 relative z-10">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <Card className="border-0 rounded-3xl shadow-2xl overflow-hidden transform hover:scale-105 hover:rotate-1 transition-all bg-gradient-to-br from-orange-400 to-pink-400">
              <CardContent className="p-10 text-center">
                <div className="w-24 h-24 bg-white rounded-full flex items-center justify-center mx-auto mb-6 shadow-xl transform hover:rotate-12 transition-transform">
                  <Users className="w-12 h-12 text-orange-500" />
                </div>
                <h3 className="text-3xl font-black text-white mb-4">Друзі</h3>
                <p className="text-xl text-white font-semibold">
                  Знайомся з новими друзями
                </p>
              </CardContent>
            </Card>

            <Card className="border-0 rounded-3xl shadow-2xl overflow-hidden transform hover:scale-105 hover:rotate-1 transition-all bg-gradient-to-br from-blue-400 to-purple-400">
              <CardContent className="p-10 text-center">
                <div className="w-24 h-24 bg-white rounded-full flex items-center justify-center mx-auto mb-6 shadow-xl transform hover:rotate-12 transition-transform">
                  <Palette className="w-12 h-12 text-blue-500" />
                </div>
                <h3 className="text-3xl font-black text-white mb-4">Творчість</h3>
                <p className="text-xl text-white font-semibold">
                  Малюй та створюй
                </p>
              </CardContent>
            </Card>

            <Card className="border-0 rounded-3xl shadow-2xl overflow-hidden transform hover:scale-105 hover:rotate-1 transition-all bg-gradient-to-br from-pink-400 to-yellow-400">
              <CardContent className="p-10 text-center">
                <div className="w-24 h-24 bg-white rounded-full flex items-center justify-center mx-auto mb-6 shadow-xl transform hover:rotate-12 transition-transform">
                  <Smile className="w-12 h-12 text-pink-500" />
                </div>
                <h3 className="text-3xl font-black text-white mb-4">Радість</h3>
                <p className="text-xl text-white font-semibold">
                  Веселись кожного дня
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Photo Gallery */}
      <section className="py-20 relative z-10">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-4 bg-white/90 rounded-full px-10 py-5 shadow-2xl mb-6">
              <Camera className="w-10 h-10 text-orange-500" />
              <h2 className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-orange-500 to-pink-500">
                Наші Фото
              </h2>
            </div>
            <p className="text-2xl text-gray-700 font-semibold">
              Подивись, як ми творимо чудеса
            </p>
          </div>

          <div className="max-w-6xl mx-auto">
            <div className="grid md:grid-cols-3 gap-6">
              {images.map((image, index) => (
                <div 
                  key={index}
                  onClick={() => setSelectedImage(image)}
                  className="relative overflow-hidden rounded-3xl shadow-2xl transform hover:scale-105 transition-all border-4 border-white cursor-pointer"
                >
                  <img
                    src={image.url}
                    alt={image.alt}
                    className="w-full h-[280px] object-contain bg-gray-50"
                  />
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Details Section */}
      <section id="details" className="py-20 relative z-10">
        <div className="container mx-auto px-4">
          <div className="max-w-5xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-purple-500 mb-6">
                Важлива Інформація
              </h2>
              <p className="text-2xl text-gray-700 font-semibold">
                Все, що тобі потрібно знати
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-8 mb-8">
              <Card className="border-0 rounded-3xl shadow-2xl bg-gradient-to-br from-blue-100 to-blue-200 transform hover:scale-105 transition-all">
                <CardContent className="p-10">
                  <div className="flex items-start gap-6">
                    <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-500 rounded-3xl flex items-center justify-center flex-shrink-0 shadow-xl">
                      <Calendar className="w-10 h-10 text-white" />
                    </div>
                    <div>
                      <h3 className="text-3xl font-black text-gray-800 mb-3">Коли?</h3>
                      <p className="text-2xl text-gray-900 font-bold mb-2">Щочетверга</p>
                      <div className="flex items-center gap-3 text-xl text-gray-700 font-semibold">
                        <Clock className="w-6 h-6" />
                        <span>15:30 - 17:00</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-0 rounded-3xl shadow-2xl bg-gradient-to-br from-pink-100 to-pink-200 transform hover:scale-105 transition-all">
                <CardContent className="p-10">
                  <div className="flex items-start gap-6">
                    <div className="w-20 h-20 bg-gradient-to-br from-pink-500 to-orange-500 rounded-3xl flex items-center justify-center flex-shrink-0 shadow-xl">
                      <MapPin className="w-10 h-10 text-white" />
                    </div>
                    <div>
                      <h3 className="text-3xl font-black text-gray-800 mb-3">Де?</h3>
                      <p className="text-xl text-gray-900 font-semibold mb-2">
                        Tweede van der Helststraat 66
                      </p>
                      <p className="text-xl text-gray-900 font-semibold mb-2">1072 PG, Amsterdam</p>
                      <p className="text-lg text-gray-700 font-semibold">Кімната 13</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card className="border-0 rounded-3xl shadow-2xl bg-gradient-to-br from-green-100 to-yellow-100 transform hover:scale-105 transition-all">
              <CardContent className="p-10">
                <div className="flex items-start gap-6">
                  <div className="w-20 h-20 bg-gradient-to-br from-green-500 to-yellow-500 rounded-3xl flex items-center justify-center flex-shrink-0 shadow-xl">
                    <Euro className="w-10 h-10 text-white" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-3xl font-black text-gray-800 mb-4">Підтримка</h3>
                    <p className="text-xl text-gray-700 font-semibold leading-relaxed">
                      Підтримай наших волонтерів! Будь-який внесок допомагає
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 relative z-10 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-orange-500 via-pink-500 to-purple-500" />
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-10 left-20 w-40 h-40 bg-yellow-400 rounded-full blur-3xl animate-pulse" />
          <div className="absolute bottom-20 right-20 w-60 h-60 bg-blue-400 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}} />
        </div>
        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            <div className="mb-10 flex justify-center">
              <div className="w-48 h-48 rounded-full overflow-hidden shadow-2xl ring-8 ring-white/30 transform hover:scale-110 transition-transform">
                <img 
                  src="https://qtrypzzcjebvfcihiynt.supabase.co/storage/v1/object/public/base44-prod/public/68e796544654cada1ecae944/0d0d3cd24_Screenshot2025-10-09at133431.png"
                  alt="Oekrainse Kids Club Logo"
                  className="w-full h-full object-cover scale-110"
                />
              </div>
            </div>
            <h2 className="text-6xl md:text-7xl font-black text-white mb-8 leading-tight">
              Приєднуйся до нас
            </h2>
            <p className="text-3xl text-white mb-10 font-bold">
              Зареєструйся прямо зараз
            </p>
            <Button
              size="lg"
              onClick={() => window.open('https://forms.gle/Kr6mACYApcXdXt6S7', '_blank')}
              className="bg-white hover:bg-yellow-100 shadow-2xl text-3xl px-16 py-10 font-black rounded-full transform hover:scale-110 transition-all border-4 border-white"
            >
              <ExternalLink className="w-8 h-8 mr-4 text-pink-500" />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-500 via-pink-500 to-purple-500">
                Реєстрація тут
              </span>
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-16 bg-gray-900 text-white relative z-10">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <div className="flex items-center justify-center gap-4 mb-6">
              <div className="w-16 h-16 rounded-full overflow-hidden ring-4 ring-orange-400">
                <img 
                  src="https://qtrypzzcjebvfcihiynt.supabase.co/storage/v1/object/public/base44-prod/public/68e796544654cada1ecae944/0d0d3cd24_Screenshot2025-10-09at133431.png"
                  alt="Logo"
                  className="w-full h-full object-cover"
                />
              </div>
              <h3 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-pink-400">
                Kids Club
              </h3>
            </div>
            <p className="text-2xl text-orange-400 mb-4 font-bold">
              Український дитячий клуб творчості в Амстердамі
            </p>
            <p className="text-xl text-gray-300 mb-6 leading-relaxed font-semibold">
              Дякуємо за підтримку українського ком'юніті
            </p>
            <div className="flex items-center justify-center gap-3 text-gray-400">
              <Heart className="w-6 h-6 text-red-500 animate-pulse" />
              <span className="text-lg font-semibold">Створено з любов'ю</span>
            </div>
          </div>
        </div>
      </footer>

      {/* Image Modal */}
      {selectedImage && (
        <div 
          className="fixed inset-0 bg-black/90 z-[100] flex items-center justify-center p-4"
          onClick={() => setSelectedImage(null)}
        >
          <button
            onClick={() => setSelectedImage(null)}
            className="absolute top-4 right-4 text-white hover:text-gray-300 transition-colors"
          >
            <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
          <img
            src={selectedImage.url}
            alt={selectedImage.alt}
            className="max-w-full max-h-full object-contain"
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
    </div>
  );
}

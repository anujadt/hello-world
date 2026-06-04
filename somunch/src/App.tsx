import { useState } from "react";
import { z } from "zod";
import { toast } from "sonner";
import wordmark from "@/assets/so-munch-wordmark.png";
import lips from "@/assets/so-munch-lips.png";
import frog from "@/assets/so-munch-frog.svg";
import { supabase } from "@/integrations/supabase/client";
import { Toaster } from "@/components/ui/sonner";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";

const COUNTRY_CODES = [
  { code: "+971", label: "🇦🇪 UAE" },
  { code: "+966", label: "🇸🇦 KSA" },
  { code: "+974", label: "🇶🇦 QAT" },
  { code: "+973", label: "🇧🇭 BHR" },
  { code: "+965", label: "🇰🇼 KWT" },
  { code: "+968", label: "🇴🇲 OMN" },
  { code: "+44", label: "🇬🇧 UK" },
  { code: "+1", label: "🇺🇸 US" },
];

const waitlistSchema = z.object({
  name: z.string().trim().max(100).optional(),
  country_code: z.string().min(2).max(6),
  phone: z
    .string()
    .trim()
    .regex(/^[0-9]+$/, "Digits only please")
    .min(6, "Too short")
    .max(15, "Too long"),
});

const notifySchema = z.object({
  name: z.string().trim().min(1, "Please enter your name").max(100),
  email: z.string().trim().email("Please enter a valid email").max(255),
});

export default function App() {
  return (
    <main className="min-h-screen bg-background text-foreground overflow-x-hidden">
      <Toaster richColors position="top-center" />
      <BannerHero />
    </main>
  );
}

function BannerHero() {
  return (
    <section className="relative px-4 md:px-10 pt-4 pb-16 md:pt-8 md:pb-24 min-h-screen flex items-center">
      <div className="relative w-full max-w-[1400px] mx-auto">
        <div className="pt-4 md:pt-8 text-center">
          <img
            src={frog}
            alt="So Munch — I love cakes so munch!"
            className="mx-auto w-44 md:w-64 h-auto animate-wiggle"
          />
          <h1 className="flex justify-center">
            <span className="sr-only">so munch</span>
            <div className="w-full max-w-[900px] md:max-w-[1100px] overflow-hidden select-none pointer-events-none" style={{ aspectRatio: "5 / 1" }}>
              <img
                src={wordmark}
                alt="So Munch"
                className="w-full h-auto -mt-[12%] mb-[-12%]"
              />
            </div>
          </h1>
          <p className="mt-3 text-peach/70 text-sm md:text-base">
            A high-protein cake mix · just add water, microwave, eat.
          </p>
          <InlineNotify />
          <span className="inline-block mt-5 rounded-full bg-pink-hot/20 border border-pink-hot/50 px-4 py-1.5 text-[10px] md:text-xs uppercase tracking-[0.2em] text-peach">
            Launching online soon · UAE 🇦🇪
          </span>

          <div className="mt-10 flex flex-wrap items-center justify-center gap-6 md:gap-8 text-peach">
            <Stat n="60s" l="to make" />
            <div className="h-10 w-px bg-peach/30" />
            <Stat n="99" l="calories" />
            <div className="h-10 w-px bg-peach/30" />
            <Stat n="13g" l="protein" />
          </div>
        </div>
      </div>
    </section>
  );
}

function InlineNotify() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (loading || done) return;

    const parsed = notifySchema.safeParse({ name, email });
    if (!parsed.success) {
      toast.error(parsed.error.issues[0]?.message ?? "Please check your details");
      return;
    }

    setLoading(true);
    const { error } = await supabase.from("waitlist_signups").insert({
      name: parsed.data.name,
      email: parsed.data.email,
      country_code: "+971",
      phone: null,
      source: "inline-notify",
      user_agent:
        typeof navigator !== "undefined" ? navigator.userAgent.slice(0, 255) : null,
    });
    setLoading(false);

    if (error) {
      toast.error("Something went wrong. Try again in a sec?");
      return;
    }

    setDone(true);
    toast.success("You're on the list! 🎉");
  };

  if (done) {
    return (
      <div className="mt-6 mx-auto max-w-md rounded-2xl bg-peach text-plum p-5">
        <p className="font-display uppercase text-xl">You're in.</p>
        <p className="mt-2 text-plum/80 text-sm">
          We'll email {email} the moment we launch.
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={onSubmit} className="mt-6 mx-auto max-w-md grid gap-3 text-left">
      <label className="block">
        <span className="sr-only">Name</span>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          maxLength={100}
          required
          placeholder="Your name"
          className="w-full rounded-full bg-peach/10 border-2 border-peach/20 px-5 py-3.5 text-peach placeholder:text-peach/50 focus:outline-none focus:border-pink-hot transition-colors"
        />
      </label>
      <label className="block">
        <span className="sr-only">Email</span>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          maxLength={255}
          required
          placeholder="you@example.com"
          className="w-full rounded-full bg-peach/10 border-2 border-peach/20 px-5 py-3.5 text-peach placeholder:text-peach/50 focus:outline-none focus:border-pink-hot transition-colors"
        />
      </label>
      <button
        type="submit"
        disabled={loading}
        className="rounded-full bg-peach text-plum px-7 py-4 font-bold uppercase tracking-wider hover:bg-pink-hot hover:text-peach transition-colors disabled:opacity-60"
      >
        {loading ? "Adding you…" : "Notify me"}
      </button>
    </form>
  );
}

function NotifyDialog({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (loading || done) return;

    const parsed = notifySchema.safeParse({ name, email });
    if (!parsed.success) {
      toast.error(parsed.error.issues[0]?.message ?? "Please check your details");
      return;
    }

    setLoading(true);
    const { error } = await supabase.from("waitlist_signups").insert({
      name: parsed.data.name,
      email: parsed.data.email,
      country_code: "+971",
      phone: null,
      source: "notify-dialog",
      user_agent:
        typeof navigator !== "undefined" ? navigator.userAgent.slice(0, 255) : null,
    });
    setLoading(false);

    if (error) {
      toast.error("Something went wrong. Try again in a sec?");
      return;
    }

    setDone(true);
    toast.success("You're on the list! 🎉");
  };

  return (
    <Dialog
      open={open}
      onOpenChange={(o) => {
        onOpenChange(o);
        if (!o) {
          setTimeout(() => {
            setDone(false);
            setName("");
            setEmail("");
          }, 200);
        }
      }}
    >
      <DialogContent className="bg-peach text-plum border-none rounded-[2rem] max-w-md">
        <DialogHeader>
          <DialogTitle className="font-display uppercase text-3xl text-plum leading-none">
            Be first to munch.
          </DialogTitle>
          <DialogDescription className="text-plum/70">
            Drop your name and email — we'll let you know the moment we go live.
          </DialogDescription>
        </DialogHeader>

        {done ? (
          <div className="rounded-2xl bg-plum text-peach p-5">
            <p className="font-display uppercase text-xl">You're in.</p>
            <p className="mt-2 text-peach/80 text-sm">
              We'll email {email} the moment we launch.
            </p>
          </div>
        ) : (
          <form onSubmit={onSubmit} className="grid gap-3">
            <label className="block">
              <span className="sr-only">Name</span>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                maxLength={100}
                required
                placeholder="Your name"
                className="w-full rounded-full bg-plum/5 border-2 border-plum/15 px-5 py-3.5 text-plum placeholder:text-plum/50 focus:outline-none focus:border-pink-hot transition-colors"
              />
            </label>
            <label className="block">
              <span className="sr-only">Email</span>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                maxLength={255}
                required
                placeholder="you@example.com"
                className="w-full rounded-full bg-plum/5 border-2 border-plum/15 px-5 py-3.5 text-plum placeholder:text-plum/50 focus:outline-none focus:border-pink-hot transition-colors"
              />
            </label>
            <button
              type="submit"
              disabled={loading}
              className="mt-1 rounded-full bg-plum text-peach px-7 py-4 font-bold uppercase tracking-wider hover:bg-pink-hot transition-colors disabled:opacity-60"
            >
              {loading ? "Adding you…" : "Notify me at launch"}
            </button>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );
}

function FinalCTA() {
  return (
    <section id="waitlist" className="px-6 md:px-12 py-20 md:py-28">
      <div className="max-w-3xl mx-auto rounded-[2.5rem] bg-peach text-plum p-8 md:p-14 text-center relative overflow-hidden">
        <img src={lips} alt="" aria-hidden className="absolute -top-6 -left-6 w-24 md:w-36 rotate-[-15deg] animate-float-y opacity-90" />
        <img src={lips} alt="" aria-hidden className="absolute -bottom-8 -right-6 w-24 md:w-36 rotate-[20deg] animate-float-y opacity-90" />

        <p className="font-script text-3xl text-pink-hot">launching in the UAE 🇦🇪</p>
        <h2 className="text-[clamp(2.25rem,6vw,4rem)] uppercase mt-2 leading-[0.95]">
          Be first<br />to munch.
        </h2>
        <p className="mt-5 text-base md:text-lg text-plum/80 max-w-md mx-auto">
          Drop your number — we'll text you the second we go live with our
          launch date and a little welcome treat.
        </p>

        <WaitlistForm />

        <p className="mt-5 text-xs text-plum/60 max-w-sm mx-auto">
          We'll only use your number to text you launch updates. No spam, no
          guilt. Unsubscribe anytime.
        </p>
      </div>
    </section>
  );
}

function WaitlistForm() {
  const [name, setName] = useState("");
  const [countryCode, setCountryCode] = useState("+971");
  const [phone, setPhone] = useState("");
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (loading || done) return;

    const cleanedPhone = phone.replace(/[^0-9]/g, "");
    const parsed = waitlistSchema.safeParse({
      name: name.trim() || undefined,
      country_code: countryCode,
      phone: cleanedPhone,
    });

    if (!parsed.success) {
      toast.error(parsed.error.issues[0]?.message ?? "Please check your details");
      return;
    }

    setLoading(true);
    const { error } = await supabase.from("waitlist_signups").insert({
      name: parsed.data.name ?? null,
      country_code: parsed.data.country_code,
      phone: parsed.data.phone,
      source: "landing",
      user_agent: typeof navigator !== "undefined" ? navigator.userAgent.slice(0, 255) : null,
    });
    setLoading(false);

    if (error) {
      toast.error("Something went wrong. Try again in a sec?");
      return;
    }

    setDone(true);
    toast.success("You're on the list! 🎉");
  };

  if (done) {
    return (
      <div className="mt-8 rounded-2xl bg-plum text-peach p-6">
        <p className="font-display uppercase text-2xl">You're in.</p>
        <p className="mt-2 text-peach/80 text-sm">
          We'll text {countryCode} {phone} the moment we launch. Get a spoon ready.
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={onSubmit} className="mt-8 grid gap-3 text-left">
      <label className="block">
        <span className="sr-only">Name (optional)</span>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          maxLength={100}
          placeholder="Your name (optional)"
          className="w-full rounded-full bg-plum/5 border-2 border-plum/15 px-5 py-3.5 text-plum placeholder:text-plum/50 focus:outline-none focus:border-pink-hot transition-colors"
        />
      </label>

      <div className="flex gap-2">
        <label className="block">
          <span className="sr-only">Country code</span>
          <select
            value={countryCode}
            onChange={(e) => setCountryCode(e.target.value)}
            className="h-full rounded-full bg-plum/5 border-2 border-plum/15 px-4 py-3.5 text-plum font-bold focus:outline-none focus:border-pink-hot transition-colors"
            aria-label="Country code"
          >
            {COUNTRY_CODES.map((c) => (
              <option key={c.code} value={c.code}>
                {c.label} {c.code}
              </option>
            ))}
          </select>
        </label>
        <label className="block flex-1">
          <span className="sr-only">Phone number</span>
          <input
            type="tel"
            required
            inputMode="numeric"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            maxLength={15}
            placeholder="50 123 4567"
            className="w-full rounded-full bg-plum/5 border-2 border-plum/15 px-5 py-3.5 text-plum placeholder:text-plum/50 focus:outline-none focus:border-pink-hot transition-colors"
          />
        </label>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="mt-2 rounded-full bg-plum text-peach px-7 py-4 font-bold uppercase tracking-wider hover:bg-pink-hot transition-colors disabled:opacity-60"
      >
        {loading ? "Adding you…" : "Notify me at launch"}
      </button>
    </form>
  );
}

function Footer() {
  return (
    <footer className="px-6 md:px-12 py-10 border-t border-peach/15">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row gap-6 items-center justify-between">
        <img src={wordmark} alt="So Munch" className="h-6 w-auto" />
        <p className="text-peach/60 text-xs uppercase tracking-widest text-center">
          © {new Date().getFullYear()} So Munch · Launching in the UAE · Made to love
        </p>
        <div className="flex gap-5 text-peach/70 text-xs uppercase tracking-widest">
          <a href="#" className="hover:text-peach">Instagram</a>
          <a href="#" className="hover:text-peach">Tiktok</a>
        </div>
      </div>
    </footer>
  );
}

function Stat({ n, l }: { n: string; l: string }) {
  return (
    <div>
      <p className="font-display text-3xl md:text-4xl leading-none">{n}</p>
      <p className="text-xs uppercase tracking-widest text-peach/70 mt-1">{l}</p>
    </div>
  );
}

// The components below (NotifyDialog, FinalCTA, WaitlistForm, Footer) are ported
// from the original Lovable page but are not mounted yet — matching the live page,
// which renders only the hero. They are kept so the phone-waitlist / footer
// sections can be enabled later without rebuilding them.
void NotifyDialog;
void FinalCTA;
void Footer;

import React, { useState, useRef, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import BlurFade from "@/components/magicui/BlurFade";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { ticketApi } from "@/services/api";
import { useTicketsContext } from "@/context/TicketContext";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { ArrowLeft } from "lucide-react";


const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/**
 * Intake form page for creating a new support ticket within AppShell.
 * Performs client-side validation, connects to POST /api/tickets,
 * prevents double-submission, and redirects to the queue on success.
 */
export default function CreateTicketPage() {
  const navigate = useNavigate();
  const nameInputRef = useRef(null);
  const { refresh, addTicketToState } = useTicketsContext();

  const [formData, setFormData] = useState({
    customer_name: "",
    customer_email: "",
    subject: "",
    description: "",
  });

  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Autofocus Customer Name input and set page title when page opens
  useEffect(() => {
    document.title = "New Ticket — RelayCX";
    nameInputRef.current?.focus();
  }, []);

  const validateField = (field, value) => {
    switch (field) {
      case "customer_name":
        if (!value.trim()) return "Customer name is required";
        return "";
      case "customer_email":
        if (!value.trim()) return "Customer email is required";
        if (!EMAIL_REGEX.test(value.trim())) return "Please enter a valid email address";
        return "";
      case "subject":
        if (!value.trim()) return "Subject is required";
        return "";
      case "description":
        if (!value.trim()) return "Issue description is required";
        return "";
      default:
        return "";
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));

    // Real-time email validation without needing to submit
    if (name === "customer_email") {
      if (value.trim().length > 0) {
        if (!EMAIL_REGEX.test(value.trim())) {
          setErrors((prev) => ({ ...prev, customer_email: "Please enter a valid email address" }));
        } else {
          setErrors((prev) => ({ ...prev, customer_email: "" }));
        }
      } else if (touched.customer_email) {
        setErrors((prev) => ({ ...prev, customer_email: "Customer email is required" }));
      } else {
        setErrors((prev) => ({ ...prev, customer_email: "" }));
      }
    } else if (touched[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: validateField(name, value),
      }));
    }
  };

  const handleBlur = (e) => {
    const { name, value } = e.target;
    setTouched((prev) => ({ ...prev, [name]: true }));
    setErrors((prev) => ({
      ...prev,
      [name]: validateField(name, value),
    }));
  };

  const handleSubmit = async (e) => {
    e?.preventDefault?.();

    // Mark all fields as touched and validate
    const validationErrors = {
      customer_name: validateField("customer_name", formData.customer_name),
      customer_email: validateField("customer_email", formData.customer_email),
      subject: validateField("subject", formData.subject),
      description: validateField("description", formData.description),
    };

    setTouched({
      customer_name: true,
      customer_email: true,
      subject: true,
      description: true,
    });
    setErrors(validationErrors);

    const hasErrors = Object.values(validationErrors).some((err) => Boolean(err));
    if (hasErrors) {
      toast.error("Please fill in all required fields correctly.");
      return;
    }

    setIsSubmitting(true);

    try {
      const payload = {
        customer_name: formData.customer_name.trim(),
        customer_email: formData.customer_email.trim().toLowerCase(),
        subject: formData.subject.trim(),
        description: formData.description.trim(),
      };

      const response = await ticketApi.create(payload);
      toast.success(`Ticket ${response.ticket_id} created successfully!`);

      // Optimistically add created ticket to global context state and trigger refresh
      if (addTicketToState) {
        addTicketToState({
          ...response,
          ...payload,
          status: response.status || "Open",
          created_at: response.created_at || new Date().toISOString(),
          updated_at: response.updated_at || response.created_at || new Date().toISOString(),
          notes: [],
        });
      }
      refresh?.(true);

      navigate("/");
    } catch (err) {
      toast.error(err.message || "Failed to create ticket. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleKeyDown = (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-4xl mx-auto">
      {/* Crisp Breadcrumb Navigation */}
      <BlurFade delay={0.06}>
        <nav aria-label="Breadcrumb" className="flex items-center gap-2 text-xs">
          <Link
            to="/"
            className="inline-flex items-center gap-1.5 text-zinc-400 hover:text-white transition-all duration-micro focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 rounded-sm p-0.5"
          >
            <ArrowLeft size={13} />
            <span>Tickets</span>
          </Link>
          <span className="text-zinc-600 select-none">/</span>
          <span className="text-zinc-200 font-medium">
            New Ticket
          </span>
        </nav>
      </BlurFade>

      {/* Structured Form Workbench Card */}
      <BlurFade delay={0.12}>
        <div className="max-w-2xl relative overflow-hidden rounded-xl border border-white/[0.09] bg-[#212124] p-6 sm:p-8 shadow-2xl">
          {/* Subtle Vercel specular highlight at top edge */}
          <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-zinc-600/50 to-transparent" />

          {/* Form Header */}
          <div className="border-b border-white/[0.08] pb-5 mb-6">
            <h1 className="text-lg sm:text-xl font-semibold tracking-tight text-white">
              Create Support Ticket
            </h1>
            <p className="text-xs text-zinc-400 mt-1">
              Direct customer intake workbench. A deterministic ID will be generated automatically.
            </p>
          </div>

          <form onSubmit={handleSubmit} onKeyDown={handleKeyDown} noValidate className="space-y-5">
            {/* 2-Column Grid: Customer Name & Customer Email */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div className="space-y-1.5">
                <label
                  htmlFor="customer_name"
                  className="text-xs font-medium text-zinc-300"
                >
                  Customer Name <span className="text-zinc-500">*</span>
                </label>
                <Input
                  ref={nameInputRef}
                  autoFocus
                  id="customer_name"
                  name="customer_name"
                  type="text"
                  placeholder="e.g. Aarav Sharma"
                  value={formData.customer_name}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  disabled={isSubmitting}
                  className={cn(
                    "h-10 sm:h-9 min-h-[44px] sm:min-h-0 bg-[#17171A] border border-white/[0.09] text-zinc-100 placeholder:text-zinc-500 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 focus-visible:border-transparent transition-all duration-micro",
                    touched.customer_name && errors.customer_name && "border-red-500 focus-visible:ring-red-400"
                  )}
                />
                {touched.customer_name && errors.customer_name && (
                  <p className="text-[11px] text-red-400 font-medium">
                    {errors.customer_name}
                  </p>
                )}
              </div>

              <div className="space-y-1.5">
                <label
                  htmlFor="customer_email"
                  className="text-xs font-medium text-zinc-300"
                >
                  Customer Email <span className="text-zinc-500">*</span>
                </label>
                <Input
                  id="customer_email"
                  name="customer_email"
                  type="email"
                  placeholder="e.g. aarav@example.com"
                  value={formData.customer_email}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  disabled={isSubmitting}
                  className={cn(
                    "h-10 sm:h-9 min-h-[44px] sm:min-h-0 bg-[#17171A] border border-white/[0.09] text-zinc-100 placeholder:text-zinc-500 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 focus-visible:border-transparent transition-all duration-micro",
                    (touched.customer_email || formData.customer_email.trim().length > 0) && errors.customer_email && "border-red-500 focus-visible:ring-red-400"
                  )}
                />
                {(touched.customer_email || formData.customer_email.trim().length > 0) && errors.customer_email && (
                  <p className="text-[11px] text-red-400 font-medium">
                    {errors.customer_email}
                  </p>
                )}
              </div>
            </div>

            {/* Subject */}
            <div className="space-y-1.5">
              <label
                htmlFor="subject"
                className="text-xs font-medium text-zinc-300"
              >
                Subject <span className="text-zinc-500">*</span>
              </label>
              <Input
                id="subject"
                name="subject"
                type="text"
                placeholder="Brief summary of the issue..."
                value={formData.subject}
                onChange={handleChange}
                onBlur={handleBlur}
                disabled={isSubmitting}
                className={cn(
                  "h-10 sm:h-9 min-h-[44px] sm:min-h-0 bg-[#17171A] border border-white/[0.09] text-zinc-100 placeholder:text-zinc-500 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 focus-visible:border-transparent transition-all duration-micro",
                  touched.subject && errors.subject && "border-red-500 focus-visible:ring-red-400"
                )}
              />
              {touched.subject && errors.subject && (
                <p className="text-[11px] text-red-400 font-medium">
                  {errors.subject}
                </p>
              )}
            </div>

            {/* Description */}
            <div className="space-y-1.5">
              <label
                htmlFor="description"
                className="text-xs font-medium text-zinc-300"
              >
                Issue Description <span className="text-zinc-500">*</span>
              </label>
              <Textarea
                id="description"
                name="description"
                rows={5}
                placeholder="Provide detailed description of the inquiry, steps to reproduce, or requested assistance..."
                value={formData.description}
                onChange={handleChange}
                onBlur={handleBlur}
                disabled={isSubmitting}
                className={cn(
                  "bg-[#17171A] border border-white/[0.09] text-zinc-100 placeholder:text-zinc-500 text-sm resize-y min-h-[110px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 focus-visible:border-transparent transition-all duration-micro",
                  touched.description && errors.description && "border-red-500 focus-visible:ring-red-400"
                )}
              />
              {touched.description && errors.description && (
                <p className="text-[11px] text-red-400 font-medium">
                  {errors.description}
                </p>
              )}
            </div>

            {/* Form Actions with Vercel Buttons */}
            <div className="pt-4 border-t border-white/[0.08] flex items-center justify-end gap-3">
              <Link
                to="/"
                className="inline-flex items-center justify-center min-h-[44px] sm:min-h-0 h-10 sm:h-8 px-4 rounded-md border border-zinc-800 bg-zinc-900 text-zinc-300 hover:bg-zinc-800 hover:text-white active:scale-[0.98] text-xs font-medium transition-all duration-micro focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 cursor-pointer select-none shadow-sm"
              >
                Cancel
              </Link>

              <button
                type="submit"
                disabled={isSubmitting}
                title="Create Ticket (⌘↵)"
                className="inline-flex items-center justify-center gap-1.5 min-h-[44px] sm:min-h-0 h-10 sm:h-8 px-4 rounded-md bg-white hover:bg-zinc-200 text-black text-xs font-medium transition-all duration-micro select-none shadow-sm cursor-pointer active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 focus-visible:ring-offset-2 focus-visible:ring-offset-black disabled:opacity-40 disabled:cursor-not-allowed"
              >
                {isSubmitting ? (
                  <span className="inline-flex items-center gap-2">
                    <svg className="animate-spin h-3.5 w-3.5 text-black" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                    </svg>
                    Creating Ticket...
                  </span>
                ) : (
                  <>
                    <span>Create Ticket</span>
                    <kbd className="hidden sm:inline-block font-mono text-[10px] text-zinc-600 bg-zinc-200 px-1 py-0.5 rounded border border-zinc-300 select-none">
                      ⌘↵
                    </kbd>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </BlurFade>
    </div>
  );
}


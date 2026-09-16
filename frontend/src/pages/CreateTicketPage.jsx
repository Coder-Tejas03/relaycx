import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import AppHeader from "@/components/layout/AppHeader";
import BlurFade from "@/components/magicui/BlurFade";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { ticketApi } from "@/services/api";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/**
 * Intake form page for creating a new support ticket.
 * Performs client-side validation, connects to POST /api/tickets,
 * prevents double-submission, and redirects to the queue on success.
 */
export default function CreateTicketPage() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    customer_name: "",
    customer_email: "",
    subject: "",
    description: "",
  });

  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

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

    if (touched[name]) {
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
    e.preventDefault();

    // Mark all as touched and validate
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
      toast.error("Please resolve the highlighted form errors before submitting.");
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
      navigate("/");
    } catch (err) {
      toast.error(err.message || "Failed to create ticket. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#09090B] text-zinc-100 antialiased selection:bg-indigo-500/30 selection:text-indigo-200">
      <AppHeader />

      <main className="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:px-8 space-y-6">
        <BlurFade delay={0.08}>
          <div>
            <Link
              to="/"
              className="inline-flex items-center gap-1.5 text-xs font-medium text-zinc-400 transition-colors hover:text-white group"
            >
              <span className="transition-transform group-hover:-translate-x-0.5">←</span>
              Back to Tickets Queue
            </Link>
          </div>
        </BlurFade>

        <BlurFade delay={0.16}>
          <Card className="border-zinc-800/80 bg-zinc-900/60 shadow-2xl backdrop-blur-sm">
            <CardHeader className="border-b border-zinc-800/80 pb-5">
              <CardTitle className="text-xl font-bold tracking-tight text-white">
                Create New Support Ticket
              </CardTitle>
              <CardDescription className="text-xs sm:text-sm text-zinc-400 mt-1">
                Log an incoming customer inquiry. Provide accurate details so the support team can triage effectively.
              </CardDescription>
            </CardHeader>

            <CardContent className="pt-6">
              <form onSubmit={handleSubmit} noValidate className="space-y-5">
                {/* 2-Column Grid: Customer Name & Customer Email */}
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div className="space-y-1.5">
                    <label
                      htmlFor="customer_name"
                      className="text-xs font-semibold text-zinc-300"
                    >
                      Customer Name <span className="text-indigo-400">*</span>
                    </label>
                    <Input
                      id="customer_name"
                      name="customer_name"
                      type="text"
                      placeholder="e.g. Aarav Sharma"
                      value={formData.customer_name}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      disabled={isSubmitting}
                      className={cn(
                        "h-10 bg-zinc-950/60 border-zinc-800 text-zinc-100 placeholder:text-zinc-600 focus-visible:ring-indigo-500/40 text-sm",
                        touched.customer_name && errors.customer_name && "border-red-500/80 focus-visible:ring-red-500/40"
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
                      className="text-xs font-semibold text-zinc-300"
                    >
                      Customer Email <span className="text-indigo-400">*</span>
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
                        "h-10 bg-zinc-950/60 border-zinc-800 text-zinc-100 placeholder:text-zinc-600 focus-visible:ring-indigo-500/40 text-sm",
                        touched.customer_email && errors.customer_email && "border-red-500/80 focus-visible:ring-red-500/40"
                      )}
                    />
                    {touched.customer_email && errors.customer_email && (
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
                    className="text-xs font-semibold text-zinc-300"
                  >
                    Subject <span className="text-indigo-400">*</span>
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
                      "h-10 bg-zinc-950/60 border-zinc-800 text-zinc-100 placeholder:text-zinc-600 focus-visible:ring-indigo-500/40 text-sm",
                      touched.subject && errors.subject && "border-red-500/80 focus-visible:ring-red-500/40"
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
                    className="text-xs font-semibold text-zinc-300"
                  >
                    Issue Description <span className="text-indigo-400">*</span>
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
                      "bg-zinc-950/60 border-zinc-800 text-zinc-100 placeholder:text-zinc-600 focus-visible:ring-indigo-500/40 text-sm resize-y min-h-[120px]",
                      touched.description && errors.description && "border-red-500/80 focus-visible:ring-red-500/40"
                    )}
                  />
                  {touched.description && errors.description && (
                    <p className="text-[11px] text-red-400 font-medium">
                      {errors.description}
                    </p>
                  )}
                </div>

                {/* Submit button & actions */}
                <div className="pt-3 flex items-center justify-end gap-3">
                  <Link to="/">
                    <Button
                      type="button"
                      variant="outline"
                      disabled={isSubmitting}
                      className="border-zinc-800 bg-zinc-900/60 text-zinc-300 hover:bg-zinc-800 hover:text-white text-xs"
                    >
                      Cancel
                    </Button>
                  </Link>

                  <Button
                    type="submit"
                    disabled={isSubmitting}
                    className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-6 shadow-md shadow-indigo-600/30 cursor-pointer disabled:opacity-50"
                  >
                    {isSubmitting ? (
                      <span className="inline-flex items-center gap-2">
                        <svg className="animate-spin h-3.5 w-3.5 text-white" viewBox="0 0 24 24" fill="none">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                        </svg>
                        Creating Ticket...
                      </span>
                    ) : (
                      "Create Ticket"
                    )}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </BlurFade>
      </main>
    </div>
  );
}

import React from "react";
import { AnimatePresence, motion } from "motion/react";
import { cn } from "@/lib/utils";

/**
 * AnimatedList renders children with smooth entry and layout transitions.
 */
export function AnimatedList({
  children,
  className,
}) {
  const childrenArray = React.Children.toArray(children);

  return (
    <div className={cn("flex flex-col gap-3", className)}>
      <AnimatePresence initial={false}>
        {childrenArray.map((item, index) => (
          <motion.div
            key={item.key || index}
            initial={{ scale: 0.96, opacity: 0, y: 10 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.96, opacity: 0, y: -10 }}
            transition={{ type: "spring", stiffness: 350, damping: 25 }}
            layout
          >
            {item}
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}

export default AnimatedList;

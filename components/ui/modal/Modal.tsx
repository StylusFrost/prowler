import {
  Button,
  Modal as ModalContainer,
  ModalBody,
  ModalContent,
  ModalFooter,
  ModalHeader,
} from "@nextui-org/react";
import React from "react";

interface ModalProps {
  title: string;
  isOpen: boolean;
  onOpenChange: (isOpen: boolean) => void;
  body: React.ReactNode;
  onCloseText?: string;
  actionText?: string;
  onAction?: () => void;
  isDismissable?: boolean;
}

export const Modal: React.FC<ModalProps> = ({
  title,
  isOpen,
  onOpenChange,
  body,
  onCloseText = "Close",
  actionText = "Save",
  onAction,
  isDismissable = true,
}) => {
  const hasActionButton = actionText && onAction;

  return (
    <>
      <ModalContainer
        isOpen={isOpen}
        onOpenChange={onOpenChange}
        backdrop="blur"
        isDismissable={isDismissable}
        isKeyboardDismissDisabled={!isDismissable}
        hideCloseButton={!isDismissable}
      >
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader className="flex flex-col gap-1">{title}</ModalHeader>
              <ModalBody>{body}</ModalBody>
              <ModalFooter>
                <Button color="danger" variant="light" onPress={onClose}>
                  {onCloseText && onCloseText}
                </Button>
                {hasActionButton && (
                  <Button color="primary" onPress={onAction}>
                    {actionText}
                  </Button>
                )}
              </ModalFooter>
            </>
          )}
        </ModalContent>
      </ModalContainer>
    </>
  );
};

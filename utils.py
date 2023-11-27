import logging
import socket
from dataclasses import dataclass
from typing import Any

from google.api_core.exceptions import GoogleAPICallError
from google.api_core.extended_operation import ExtendedOperation
from google.cloud import compute_v1

def get_logger(name:str) :
    return logging.getLogger(f"[{socket.gethostname()}]{name}")

#The logger's name is constructed by formatting a string with the hostname obtained from socket.gethostname() and the provided name parameter.

GCP_UTILS_LOGGER = get_logger(__name__)


def wait_for_extended_operation(
    operation: ExtendedOperation, verbose_name: str = "operation", timeout: int = 300
) -> Any:
    try:
        result = operation.result(timeout=timeout)
    except GoogleAPICallError as ex:
        GCP_UTILS_LOGGER.exception("Exception occurred")
        for attr in ["details", "domain", "errors", "metadata", "reason", "response"]:
            value = getattr(ex, attr, None)
            if value:
                GCP_UTILS_LOGGER.error(f"ex.{attr}:\n{value}")
        if isinstance(ex.response, compute_v1.Operation):
            for error in ex.response.error.errors:
                GCP_UTILS_LOGGER.error(f"Error message: {error.message}")

        raise RuntimeError("Exception during extended operation") from ex

    if operation.error_code:
        GCP_UTILS_LOGGER.error(
            f"Error during {verbose_name}: [Code: {operation.error_code}]: {operation.error_message}"
        )
        GCP_UTILS_LOGGER.error(f"Operation ID: {operation.name}")
        raise operation.exception() or RuntimeError(operation.error_message)

    if operation.warnings:
        GCP_UTILS_LOGGER.warning(f"Warnings during {verbose_name}:\n")
        for warning in operation.warnings:
            GCP_UTILS_LOGGER.warning(f" - {warning.code}: {warning.message}")

    return result
